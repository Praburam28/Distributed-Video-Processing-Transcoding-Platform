
import asyncio
import json
import subprocess
from pathlib import Path
from datetime import datetime

from sqlalchemy.orm import Session

from shared.database import SessionLocal, init_db
from shared.models import (
    ProcessingJob,
    ProcessingAttempt,
    TranscodingOutput,
    Video,
)
from shared.messaging import consume, publish
from shared.config import settings


init_db()

RES_HEIGHT = {
    "360p": 360,
    "720p": 720,
    "1080p": 1080,
}

OUT = Path(settings.output_dir)
OUT.mkdir(parents=True, exist_ok=True)


async def handle(message):
    async with message.process(requeue=False):
        payload = json.loads(message.body)

        job_id = payload["job_id"]
        video_id = payload["video_id"]
        input_path = payload["input_path"]

        # Redis idempotency lock
        import redis

        r = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

        if r.get(f"job:{job_id}:done"):
            return

        db: Session = SessionLocal()
        attempt_no = 1

        try:
            job = db.get(ProcessingJob, job_id)

            if not job:
                return

            if job.status == "completed":
                r.set(f"job:{job_id}:done", "1")
                return

            attempt_no = job.retry_count + 1

            attempt = ProcessingAttempt(
                job_id=job_id,
                attempt_number=attempt_no,
                status="running",
            )

            db.add(attempt)

            job.status = "processing"
            job.progress = 5

            db.commit()

            outputs = []

            for res in payload.get(
                "resolutions",
                ["360p", "720p"],
            ):
                height = RES_HEIGHT.get(res)

                if not height:
                    continue

                target = (
                    OUT
                    / video_id
                    / job_id
                    / f"{res}.mp4"
                )

                target.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    input_path,

                    # Explicitly map the first video stream.
                    "-map",
                    "0:v:0",

                    # Explicitly map the first audio stream if present.
                    "-map",
                    "0:a:0?",

                    # Resize video while maintaining aspect ratio.
                    "-vf",
                    f"scale=-2:{height}",

                    # Video encoding.
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "23",

                    # Preserve audio by encoding it as AAC.
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-ac",
                    "2",

                    # Improve MP4 playback compatibility.
                    "-movflags",
                    "+faststart",

                    str(target),
                ]

                print(
                    f"Starting transcoding: "
                    f"{video_id} - {res}"
                )

                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600,
                )

                if proc.returncode != 0:
                    raise RuntimeError(
                        proc.stderr[-3000:]
                    )

                outputs.append(
                    (
                        res,
                        str(target),
                        target.stat().st_size,
                    )
                )

            for res, path, size in outputs:
                exists = (
                    db.query(TranscodingOutput)
                    .filter_by(
                        video_id=video_id,
                        job_id=job_id,
                        resolution=res,
                    )
                    .first()
                )

                if not exists:
                    db.add(
                        TranscodingOutput(
                            video_id=video_id,
                            job_id=job_id,
                            resolution=res,
                            file_path=path,
                            file_size=size,
                        )
                    )

            attempt.status = "completed"
            attempt.finished_at = datetime.utcnow()

            job.status = "completed"
            job.progress = 100
            job.error_message = None

            video = db.get(Video, video_id)

            if video:
                video.status = "completed"

            db.commit()

            r.set(f"job:{job_id}:done", "1")

            await publish(
                "transcode.completed",
                {
                    "job_id": job_id,
                    "video_id": video_id,
                },
            )

        except Exception as exc:
            db.rollback()

            job = db.get(ProcessingJob, job_id)

            if job:
                job.retry_count += 1
                job.error_message = str(exc)

                job.status = (
                    "failed"
                    if job.retry_count >= job.max_retries
                    else "retrying"
                )

                db.commit()

                if job.retry_count < job.max_retries:
                    await publish(
                        "transcode.requested",
                        {
                            **payload,
                            "retry_count": job.retry_count,
                        },
                        routing_key="transcode.requested",
                    )
                else:
                    await publish(
                        "transcode.dead",
                        {
                            "job_id": job_id,
                            "video_id": video_id,
                            "error": str(exc),
                        },
                    )

        finally:
            db.close()


async def main():
    connection = await consume(
        "transcode.requested",
        handle,
    )

    await connection.connected.wait()

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
