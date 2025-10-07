# Form Pipeline Backend

FastAPI backend with Playwright for automated form submissions.

## Features

- Spreadsheet validation and cleaning
- Automated form filling with Playwright
- Real-time progress tracking
- Pause/Resume/Kill controls

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

6. API available at [http://localhost:8000](http://localhost:8000)
7. API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /clean` - Clean and validate spreadsheet
- `POST /submit` - Start form submissions
- `GET /status` - Get submission progress
- `POST /pause` - Pause submission
- `POST /resume` - Resume submission
- `POST /kill` - Stop submission

## Docker Build (Local Testing)

```bash
docker build -t form-pipeline-backend .
docker run -p 8000:8000 form-pipeline-backend
```

## Deployment to Google Cloud Run

### Prerequisites

- Google Cloud SDK installed
- Project created in Google Cloud Console
- Cloud Run API enabled

### Deploy Steps

1. Authenticate with Google Cloud:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. Build and push container:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/form-pipeline-backend
```

3. Deploy to Cloud Run:
```bash
gcloud run deploy form-pipeline-backend \
  --image gcr.io/YOUR_PROJECT_ID/form-pipeline-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 3600
```

4. Note the service URL and add it to frontend `.env`:
```
NEXT_PUBLIC_API_URL=https://your-service-url.run.app
```

## Environment Variables

- `ENV`: Environment (development/production)
- `PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins

## Tech Stack

- FastAPI
- Playwright
- Pandas & OpenPyXL
- Uvicorn (ASGI server)

