# 🎬 Distributed Video Processing & Transcoding Platform

<p align="center">
  <strong>A Scalable Microservices-Based Video Processing and Transcoding System</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-blue?logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react" />
  <img src="https://img.shields.io/badge/TypeScript-Frontend-3178C6?logo=typescript" />
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql" />
  <img src="https://img.shields.io/badge/RabbitMQ-Messaging-FF6600?logo=rabbitmq" />
  <img src="https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker" />
</p>

---

## 📌 Project Overview

The **Distributed Video Processing & Transcoding Platform** is a full-stack application designed to process and transcode videos using independently deployable Python microservices.

The platform allows users to upload videos, process them asynchronously, generate thumbnails, and convert videos into multiple resolutions using FFmpeg.

RabbitMQ handles asynchronous communication between services, while Redis supports caching and job coordination.

The application provides a React dashboard to upload videos, monitor processing progress, view job statuses, and play processed video outputs.

## 🎯 Objectives

- Build a distributed video processing system using Python microservices.
- Support asynchronous video uploads and processing.
- Generate multiple video resolutions.
- Automatically generate video thumbnails.
- Track video metadata and processing lifecycle.
- Implement reliable message processing and retry mechanisms.
- Provide a professional web dashboard for video management.
- Deploy services using Docker and Docker Compose.

## ✨ Key Features

### 🎥 Video Upload Management
- Upload video files through a web interface.
- Validate supported video formats and file sizes.
- Generate unique video identifiers.
- Store uploaded videos and metadata.

### ⚙️ Distributed Video Processing
- Independently deployable Python microservices.
- Asynchronous job processing using RabbitMQ.
- Background video transcoding using FFmpeg.
- Support for configurable resolutions:
  - 360p
  - 720p
  - 1080p

### 🖼️ Thumbnail Generation
- Extract video frames using FFmpeg.
- Generate thumbnail images.
- Store thumbnail references.

### 📊 Processing Management
- Track processing job status.
- Record processing attempts.
- Handle processing failures.
- Support retry mechanisms.
- Protect against duplicate job processing.

### ▶️ Media Delivery
- Access processed videos.
- Retrieve available resolutions.
- Preview generated thumbnails.
- Play transcoded video outputs.

### 💻 Dashboard
- Video upload interface.
- Uploaded video library.
- Processing status indicators.
- Job failure information.
- Available resolution details.
- Video playback and thumbnail previews.

## 🏗️ System Architecture

The application consists of seven independent microservices.

| Microservice | Responsibility |
|---|---|
| API Gateway | Single entry point for frontend requests |
| Video Upload Service | Upload validation and file storage |
| Metadata Service | Video metadata management |
| Transcoding Orchestrator | Processing job coordination |
| Transcoding Worker | FFmpeg video conversion |
| Thumbnail Service | Thumbnail generation |
| Media Delivery Service | Processed media access |

### Architecture Flow

```text
                  React Frontend
                        |
                        v
                  API Gateway
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
     Upload Service  Metadata     Media Delivery
          |           Service          |
          v                            v
      MySQL DB                    Video Outputs
          |
          v
      RabbitMQ
          |
          v
 Transcoding Orchestrator
          |
          v
   RabbitMQ Job Queue
          |
          v
  Transcoding Worker
          |
          +-----------> FFmpeg
          |
          +-----------> Redis
          |
          v
   Processed Videos
          |
          v
  Thumbnail Generation
          |
          v
    Media Delivery
```

**Communication:**
- Synchronous communication: HTTP REST APIs.
- Asynchronous communication: RabbitMQ.
- Caching and job coordination: Redis.
- Database persistence: MySQL.
- Video processing: FFmpeg.

## 🛠️ Technology Stack

### Backend
- Python 3.14
- FastAPI
- SQLAlchemy ORM
- Pydantic
- Alembic

### Frontend
- React.js
- TypeScript
- Vite
- CSS

### Database and Messaging
- MySQL 8.0
- RabbitMQ
- Redis

### Video Processing
- FFmpeg

### DevOps and Testing
- Docker
- Docker Compose
- Pytest
- Git
- Visual Studio Code

## 📂 Project Structure

```text
distributed-video-processing-platform/
│
├── services/
│   ├── api_gateway/
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   ├── upload_service/
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   ├── metadata_service/
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   ├── orchestrator_service/
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   ├── transcoding_worker/
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   ├── thumbnail_service/
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   └── media_delivery/
│       ├── main.py
│       └── Dockerfile
│
├── shared/
│   ├── config.py
│   ├── database.py
│   ├── messaging.py
│   ├── models.py
│   └── schemas.py
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── package.json
│   └── Dockerfile
│
├── migrations/
├── tests/
│   ├── test_schemas.py
│   ├── test_upload_validation.py
│   └── test_job_idempotency.py
│
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Prerequisites

Install the following:

- Python 3.14
- Node.js
- Docker Desktop
- Visual Studio Code
- Git

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/distributed-video-processing-platform.git
```

```bash
cd distributed-video-processing-platform
```

### 3. Create Python Virtual Environment

**Windows PowerShell:**

```powershell
py -3.14 -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy the example configuration:

**Windows:**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Update database, RabbitMQ, Redis, and storage configuration as required.

### 6. Start Docker Services

Make sure Docker Desktop is running.

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

### 7. Access the Application

| Application | URL |
|---|---|
| React Dashboard | http://localhost:5173 |
| API Gateway Swagger | http://localhost:8000/docs |
| RabbitMQ Management | http://localhost:15672 |

Default RabbitMQ development credentials:

```text
Username: guest
Password: guest
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/videos/upload` | Upload a video |
| GET | `/videos` | Retrieve uploaded videos |
| GET | `/videos/{video_id}` | Get video details |
| GET | `/videos/{video_id}/status` | Check processing status |
| POST | `/videos/{video_id}/process` | Start video processing |
| GET | `/jobs/{job_id}` | Retrieve job details |
| GET | `/videos/{video_id}/outputs` | Retrieve transcoded outputs |
| GET | `/videos/{video_id}/thumbnails` | Retrieve thumbnails |

**API Documentation:** Available through FastAPI Swagger UI.

## 🧪 Testing

Run the automated test suite:

```bash
pytest -v
```

Run a specific test:

```bash
pytest tests/test_upload_validation.py -v
```

Run tests with coverage:

```bash
pip install pytest-cov
pytest --cov=services --cov=shared --cov-report=html
```

The included tests cover basic upload validation, schema validation, and job idempotency behavior. Full distributed integration and end-to-end testing remain additional verification tasks.

## 🔄 Video Processing Workflow

1. User uploads a video through the React dashboard.
2. Upload Service validates the file.
3. Video metadata is stored.
4. An upload event is published through RabbitMQ.
5. Transcoding Orchestrator creates a processing job.
6. Transcoding Worker consumes the job.
7. FFmpeg generates the requested video resolutions.
8. Thumbnail Service generates preview images.
9. Processing results are recorded.
10. Media Delivery Service provides access to the processed outputs.
11. Dashboard displays processing information and available videos.

## 🐳 Docker Commands

Start the application:

```bash
docker compose up -d
```

Rebuild containers:

```bash
docker compose up --build -d
```

View container status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop containers:

```bash
docker compose down
```

Stop containers and remove persistent volumes:

```bash
docker compose down -v
```

**Warning:** The last command permanently removes the Docker volumes containing persistent application data.

## 🚀 Future Enhancements

- Service-owned databases and independent migrations.
- Reliable RabbitMQ retry and dead-letter queues.
- Atomic job locking and idempotent processing.
- Real-time progress updates using WebSockets.
- Video streaming with HTTP range requests.
- Authentication and role-based access control.
- Cloud object storage integration.
- Kubernetes deployment.
- Distributed monitoring and centralized logging.
- Comprehensive integration and end-to-end testing.

## 🎓 Learning Outcomes

This project demonstrates practical implementation of:

- Python microservices architecture.
- REST API development using FastAPI.
- Asynchronous message-driven processing.
- RabbitMQ message queues.
- Redis-based job coordination.
- Video processing with FFmpeg.
- Database integration using SQLAlchemy.
- React and TypeScript frontend development.
- Docker-based application deployment.
- Automated testing with Pytest.

## 👨‍💻 Author

**Praburam R**

Python Developer

---

<p align="center">
  <strong>Built with Python, FastAPI, React, RabbitMQ, Redis and FFmpeg ❤️</strong>
</p>
