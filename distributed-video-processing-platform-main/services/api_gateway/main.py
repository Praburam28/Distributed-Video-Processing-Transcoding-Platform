
import httpx

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings


app = FastAPI(
    title="Distributed Video Platform API Gateway",
    version="1.0.0",
    description="Single entry point routing requests to independently deployable services.",
)

# CORS configuration: allow requests from the Vite frontend
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


@app.get("/health")
def health():
    return {"service": "api-gateway", "status": "ok"}


@app.post("/videos/upload", status_code=201)
async def upload_video(file: UploadFile = File(...)):
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            response = await client.post(
                f"{settings.upload_service_url}/videos/upload",
                files={
                    "file": (
                        file.filename,
                        file.file,
                        file.content_type,
                    )
                },
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text,
            )

        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=str(e))


@app.get("/videos")
async def list_videos():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.upload_service_url}/videos"
        )
        response.raise_for_status()
        return response.json()


@app.get("/videos/{video_id}")
async def get_video(video_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.upload_service_url}/videos/{video_id}"
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Video not found")

        response.raise_for_status()
        video = response.json()

        metadata_response = await client.get(
            f"{settings.metadata_service_url}/videos/{video_id}/metadata"
        )

        video["metadata"] = (
            metadata_response.json()
            if metadata_response.status_code == 200
            else None
        )

        return video


@app.get("/videos/{video_id}/status")
async def video_status(video_id: str):
    async with httpx.AsyncClient() as client:
        video_response = await client.get(
            f"{settings.upload_service_url}/videos/{video_id}"
        )

        if video_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Video not found")

        jobs_response = await client.get(
            f"{settings.orchestrator_url}/jobs/by-video/{video_id}"
        )

        return {
            "video_id": video_id,
            "video_status": video_response.json().get("status"),
            "jobs": (
                jobs_response.json()
                if jobs_response.status_code == 200
                else []
            ),
        }


@app.post("/videos/{video_id}/process", status_code=202)
async def process_video(
    video_id: str,
    resolutions: list[str] = Query(default=["360p", "720p"]),
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.orchestrator_url}/videos/{video_id}/process",
            json={"resolutions": resolutions},
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Video not found")

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text,
            )

        return response.json()


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.orchestrator_url}/jobs/{job_id}"
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Job not found")

        response.raise_for_status()
        return response.json()


@app.get("/videos/{video_id}/outputs")
async def outputs(video_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.delivery_service_url}/videos/{video_id}/outputs"
        )
        response.raise_for_status()
        return response.json()


@app.get("/videos/{video_id}/thumbnails")
async def thumbnails(video_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.delivery_service_url}/videos/{video_id}/thumbnails"
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Thumbnail not found")

        response.raise_for_status()
        return response.json()
