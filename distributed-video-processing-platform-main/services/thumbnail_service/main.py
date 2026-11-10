import subprocess
from pathlib import Path
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal, init_db
from shared.models import Video, VideoThumbnail
from shared.config import settings

app=FastAPI(title="Thumbnail Generation Service",version="1.0.0")
init_db()
THUMBS=Path(settings.thumbnail_dir); THUMBS.mkdir(parents=True,exist_ok=True)

@app.get("/health")
def health(): return {"service":"thumbnail-service","status":"ok"}

@app.post("/videos/{video_id}/thumbnails",status_code=201)
def create_thumbnail(video_id: str, at_seconds: float=1.0):
    db:Session=SessionLocal()
    try:
        video=db.get(Video,video_id)
        if not video: raise HTTPException(404,"Video not found")
        target=THUMBS/f"{video_id}.jpg"
        cmd=["ffmpeg","-y","-ss",str(max(at_seconds,0)),"-i",video.stored_path,"-frames:v","1","-q:v","2",str(target)]
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        if proc.returncode: raise HTTPException(422,proc.stderr[-1000:])
        row=db.query(VideoThumbnail).filter_by(video_id=video_id).first()
        if row: row.file_path=str(target); row.timestamp_seconds=at_seconds
        else: db.add(VideoThumbnail(video_id=video_id,file_path=str(target),timestamp_seconds=at_seconds))
        db.commit()
        return {"video_id":video_id,"thumbnail_url":f"/media/thumbnails/{video_id}.jpg","timestamp_seconds":at_seconds}
    finally: db.close()

@app.get("/videos/{video_id}/thumbnails")
def get_thumbnail(video_id: str):
    db=SessionLocal()
    try:
        row=db.query(VideoThumbnail).filter_by(video_id=video_id).first()
        if not row: raise HTTPException(404,"Thumbnail not generated")
        return {"video_id":video_id,"thumbnail_url":f"/media/thumbnails/{video_id}.jpg","timestamp_seconds":row.timestamp_seconds}
    finally: db.close()
