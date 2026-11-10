import os, uuid, mimetypes
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal, init_db
from shared.models import Video
from shared.config import settings
from shared.messaging import publish

app = FastAPI(title="Video Upload Service", version="1.0.0")
init_db()
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {x.strip().lower() for x in settings.allowed_extensions.split(",")}

@app.get("/health")
def health(): return {"service":"upload-service","status":"ok"}

@app.post("/videos/upload", status_code=201)
async def upload_video(file: UploadFile = File(...)):
    filename = Path(file.filename or "upload").name
    ext = filename.rsplit(".",1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED:
        raise HTTPException(415, f"Unsupported file extension. Allowed: {sorted(ALLOWED)}")
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit")
    video_id = str(uuid.uuid4())
    dest = UPLOAD_DIR / f"{video_id}.{ext}"
    dest.write_bytes(data)
    db: Session = SessionLocal()
    try:
        row = Video(id=video_id, original_filename=filename, stored_path=str(dest),
                    content_type=file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream",
                    file_size=len(data), status="uploaded")
        db.add(row); db.commit()
    except Exception:
        db.rollback(); dest.unlink(missing_ok=True); raise
    finally: db.close()
    await publish("video.uploaded", {"video_id":video_id,"path":str(dest),"filename":filename})
    return {"video_id":video_id,"filename":filename,"size":len(data),"status":"uploaded"}

@app.get("/videos")
def list_videos():
    db=SessionLocal()
    try:
        return [{"video_id":v.id,"filename":v.original_filename,"size":v.file_size,"status":v.status,"created_at":v.created_at} for v in db.query(Video).order_by(Video.created_at.desc()).all()]
    finally: db.close()

@app.get("/videos/{video_id}")
def get_video(video_id: str):
    db=SessionLocal()
    try:
        v=db.get(Video,video_id)
        if not v: raise HTTPException(404,"Video not found")
        return {"video_id":v.id,"filename":v.original_filename,"size":v.file_size,"status":v.status,"created_at":v.created_at}
    finally: db.close()
