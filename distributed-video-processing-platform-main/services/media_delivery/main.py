
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.database import SessionLocal, init_db
from shared.models import TranscodingOutput, VideoThumbnail
from shared.config import settings


app = FastAPI(
    title="Media Delivery Service",
    version="1.0.0",
)

# Allow the React frontend to access media APIs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.get("/health")
def health():
    return {
        "service": "media-delivery",
        "status": "ok",
    }


@app.get("/videos/{video_id}/outputs")
def outputs(video_id: str):
    db: Session = SessionLocal()

    try:
        rows = (
            db.query(TranscodingOutput)
            .filter_by(video_id=video_id)
            .all()
        )

        return [
            {
                "resolution": row.resolution,
                "url": (
                    f"/media/videos/{video_id}/"
                    f"{row.job_id}/{row.resolution}.mp4"
                ),
                "size": row.file_size,
            }
            for row in rows
        ]

    finally:
        db.close()


@app.get("/videos/{video_id}/thumbnails")
def thumbnails(video_id: str):
    db: Session = SessionLocal()

    try:
        row = (
            db.query(VideoThumbnail)
            .filter_by(video_id=video_id)
            .first()
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Thumbnail not found",
            )

        return {
            "url": f"/media/thumbnails/{video_id}.jpg"
        }

    finally:
        db.close()


@app.get(
    "/media/videos/{video_id}/{job_id}/{resolution}.mp4"
)
def stream_output(
    video_id: str,
    job_id: str,
    resolution: str,
):
    db = SessionLocal()

    try:
        row = (
            db.query(TranscodingOutput)
            .filter_by(
                video_id=video_id,
                job_id=job_id,
                resolution=resolution,
            )
            .first()
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Output not found",
            )

        path = Path(row.file_path)

        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail="Media file missing",
            )

        return FileResponse(
            path,
            media_type="video/mp4",
            filename=path.name,
        )

    finally:
        db.close()


@app.get("/media/thumbnails/{video_id}.jpg")
def stream_thumbnail(video_id: str):
    db = SessionLocal()

    try:
        row = (
            db.query(VideoThumbnail)
            .filter_by(video_id=video_id)
            .first()
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Thumbnail not found",
            )

        path = Path(row.file_path)

        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail="Thumbnail file missing",
            )

        return FileResponse(
            path,
            media_type="image/jpeg",
        )

    finally:
        db.close()
