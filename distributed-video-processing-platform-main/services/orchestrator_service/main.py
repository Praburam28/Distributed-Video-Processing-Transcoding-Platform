import asyncio, json, uuid
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal, init_db
from shared.models import Video, ProcessingJob
from shared.schemas import ProcessRequest
from shared.messaging import publish, consume

app=FastAPI(title="Transcoding Orchestrator Service", version="1.0.0")
init_db()

@app.get("/health")
def health(): return {"service":"orchestrator-service","status":"ok"}

@app.post("/videos/{video_id}/process",status_code=202)
async def process_video(video_id: str, body: ProcessRequest=ProcessRequest()):
    db:Session=SessionLocal()
    try:
        video=db.get(Video,video_id)
        if not video: raise HTTPException(404,"Video not found")
        job=ProcessingJob(id=str(uuid.uuid4()),video_id=video_id,status="queued",progress=0)
        db.add(job); video.status="processing"; db.commit()
        payload={"job_id":job.id,"video_id":video_id,"input_path":video.stored_path,"resolutions":body.resolutions,"retry_count":0,"max_retries":job.max_retries}
    finally: db.close()
    await publish("transcode.requested",payload)
    return {"job_id":payload["job_id"],"video_id":video_id,"status":"queued","resolutions":body.resolutions}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    db=SessionLocal()
    try:
        j=db.get(ProcessingJob,job_id)
        if not j: raise HTTPException(404,"Job not found")
        return {"job_id":j.id,"video_id":j.video_id,"status":j.status,"progress":j.progress,"retry_count":j.retry_count,"max_retries":j.max_retries,"error_message":j.error_message}
    finally: db.close()

async def uploaded_handler(message):
    async with message.process():
        data=json.loads(message.body)
        # Auto-create an initial job after upload; explicit process endpoint can create another.
        await publish("video.uploaded.ack",data)

@app.on_event("startup")
async def startup():
    async def runner():
        conn=await consume("video.uploaded",uploaded_handler)
        await conn.connected.wait()
    asyncio.create_task(runner())


@app.get("/jobs/by-video/{video_id}")
def jobs_by_video(video_id: str):
    db=SessionLocal()
    try:
        return [{"job_id":j.id,"video_id":j.video_id,"status":j.status,"progress":j.progress,"retry_count":j.retry_count,"error_message":j.error_message}
                for j in db.query(ProcessingJob).filter_by(video_id=video_id).order_by(ProcessingJob.created_at.desc()).all()]
    finally: db.close()
