# Distributed Video Processing & Transcoding Platform

A microservices-based video processing platform built using Python, FastAPI, React, and FFmpeg. It supports video uploading, asynchronous transcoding, thumbnail generation, metadata management, and multi-resolution video delivery.

## Tech Stack

- **Backend:** Python (local environment), FastAPI, SQLAlchemy
- **Database:** MySQL 8
- **Message Broker:** RabbitMQ
- **Caching & State Management:** Redis
- **Video Processing:** FFmpeg
- **Frontend:** React, TypeScript, Vite
- **Containerization:** Docker, Docker Compose

## Quick Start (Windows — Git Bash)

### Prerequisites

- Python 3.12
- Node.js 20+
- Docker Desktop
- Git

### 1. Configure environment variables

Copy `.env.example` to `.env` and configure the required environment variables. The Compose stack includes MySQL, RabbitMQ, and Redis.

```bash
cp .env.example .env
```

### 2. Set up Python environment

From the project root:

```bash
python -m venv .venv
source .venv/Scripts/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Start the platform

```bash
docker compose up --build
```

### 4. Run the frontend locally (optional)

```bash
cd frontend
npm install
npm run dev
```

## Application URLs

| Component | URL |
|---|---|
| API Gateway | http://localhost:8000 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| RabbitMQ Management | http://localhost:15672 |
| React Frontend (Docker) | http://localhost:5173 |
| React Frontend (Local) | http://localhost:5174 |

## Architecture

1. The React frontend communicates with the API Gateway through HTTP.
2. The API Gateway routes upload and metadata requests to the appropriate microservices.
3. The Upload Service stores original media, creates video records, and publishes `video.uploaded` events.
4. The Orchestrator consumes upload events, creates transcoding jobs, and publishes `transcode.requested` events.
5. The Transcoding Worker consumes jobs and uses FFmpeg to generate configured video renditions.
6. The worker stores output records and processing attempts, then publishes completion or failure events.
7. The Thumbnail Service generates JPEG video previews.
8. The Media Delivery Service provides access to processed videos and thumbnails.
9. RabbitMQ supports asynchronous communication using durable queues, retry mechanisms, and dead-letter queues.
10. Redis supports idempotency locks and lightweight job state management.

## API Endpoints

### API Gateway

| Method | Endpoint | Description |
|---|---|---|
| POST | `/videos/upload` | Upload a video |
| GET | `/videos` | List uploaded videos |
| GET | `/videos/{video_id}` | Retrieve video details |
| GET | `/videos/{video_id}/status` | Check processing status |
| POST | `/videos/{video_id}/process` | Trigger video processing |
| GET | `/jobs/{job_id}` | Retrieve job details |
| GET | `/videos/{video_id}/outputs` | List transcoded outputs |
| GET | `/videos/{video_id}/thumbnails` | Retrieve thumbnail information |

Service-specific Swagger documentation is available on ports `8001`–`8006`.

## Features

- Video upload and storage
- Asynchronous video transcoding
- Multiple output resolutions (360p and 720p)
- Video metadata management
- Thumbnail generation and preview
- Job status tracking
- Microservices-based architecture
- Event-driven communication
- Retry and dead-letter handling
- Docker-based local deployment
- React frontend for upload, processing, and playback


## Verification notes

The included tests cover basic schemas, filename-extension checks, and a simplified idempotency/retry example. They are not end-to-end tests of the distributed services. Review the assignment compliance gaps before treating this project as production-ready.


## Windows PowerShell — local VS Code setup

```powershell
# From the project root
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

For the complete distributed stack, start Docker Desktop and run:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs -f
```

Open `http://localhost:5173` for the dashboard and `http://localhost:8000/docs` for the API documentation.

To stop the stack:

```powershell
docker compose down
```

To remove database, broker, and cache data as well (destructive):

```powershell
docker compose down -v
```

> Note: the Dockerfiles in this starter project still use Python 3.12. The local virtual environment command above targets Python 3.14, but Python 3.14 container compatibility must be validated before changing every service image.
