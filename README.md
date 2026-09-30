# Grow Agent

Grow Agent is a mutual-fund discovery and investment-advisory application. It combines a Next.js web interface with a FastAPI service for fund data, risk profiles, visualizations, and AI-assisted chat.

## Project Structure

- `backend/` - FastAPI API and Google ADK agent.
- `grow-agent-frontend/` - Next.js 16 / React 19 web application.
- `data/` - processed fund data and scoring weights.
- `raw_data/` - source scoring and evaluation data.
- `Dockerfile` - backend container image.

The frontend has additional setup notes in [`grow-agent-frontend/README.md`](grow-agent-frontend/README.md).

## Run Locally

### Backend

Requires Python 3.11+ and Google Cloud credentials with access to the configured Vertex AI models.

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
gcloud auth application-default login
```

Configure your Google Cloud project and Vertex AI location for Google ADK, then start the API:

```bash
python -m uvicorn backend.main:app --reload --port 8080
```

The API health check is available at <http://localhost:8080/healthz>, and interactive API documentation is at <http://localhost:8080/docs>.

### Frontend

In another terminal:

```bash
cd grow-agent-frontend
npm ci
NEXT_PUBLIC_BACKEND_BASE_URL=http://127.0.0.1:8080 npm run dev
```

Open <http://localhost:3000>. Set `NEXT_PUBLIC_BACKEND_BASE_URL` to the deployed API URL when building the frontend for another environment.

## API Overview

- `POST /chat` - send a message to the advisor.
- `GET /funds` and `GET /funds/{fund_name}` - retrieve fund data.
- `GET /partners` - retrieve partner information.
- `GET` and `POST /risk-profile` - read and save a risk profile.
- `GET /visualization/performance` - retrieve performance visualization data.
- `GET /healthz` - health check.

## Deployment

The backend and frontend have separate Dockerfiles. The frontend also includes a Cloud Build configuration in `grow-agent-frontend/cloudbuild.yaml`. Configure cloud credentials, project settings, and the backend URL for your deployment environment; do not commit credentials or local `.env` files.
