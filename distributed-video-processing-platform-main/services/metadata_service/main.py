from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal, init_db
from shared.models import Video, VideoMetadata
from pydantic import BaseModel

app=FastAPI(title="Video Metadata Service", version="1.0.0")
init_db()

class MetadataUpdate(BaseModel):
    title: str
    format: str="unknown"
    duration: float=0
    width: int=0
    height: int=0

@app.get("/health")
def health(): return {"service":"metadata-service","status":"ok"}

@app.put("/videos/{video_id}/metadata")
def upsert_metadata(video_id: str, body: MetadataUpdate):
    db:Session=SessionLocal()
    try:
        if not db.get(Video,video_id): raise HTTPException(404,"Video not found")
        row=db.get(VideoMetadata,video_id)
        if row:
            for k,v in body.model_dump().items(): setattr(row,k,v)
        else:
            row=VideoMetadata(video_id=video_id,**body.model_dump()); db.add(row)
        db.commit()
        return {"video_id":video_id,**body.model_dump()}
    finally: db.close()

@app.get("/videos/{video_id}/metadata")
def get_metadata(video_id: str):
    db=SessionLocal()
    try:
        row=db.get(VideoMetadata,video_id)
        if not row: raise HTTPException(404,"Metadata not found")
        return {"video_id":row.video_id,"title":row.title,"format":row.format,"duration":row.duration,"width":row.width,"height":row.height}
    finally: db.close()
