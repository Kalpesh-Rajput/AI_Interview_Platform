# Interview Intelligence Platform

AI-powered interview preparation for recruiters. Upload a **Job Description** and **Candidate Resume** to generate **10 contextual interview questions** (7 technical + 3 scenario) with recruiter-friendly explanations.

> **Not an ATS.** This platform helps recruiters know *what to ask* and *why it matters* — not score or rank candidates.

## Tech Stack

| Layer | Stack |
|-------|--------|
| Frontend | React, Tailwind CSS, Axios, React Router, Vite |
| Backend | FastAPI, Python, LangGraph |
| AI | OpenRouter API (multi-model routing) |
| Deploy | Vercel (frontend), Render (backend) |

## Architecture

```
Upload → Parsing Agent → Context Extraction → Question Generation
       → Explanation Agent → Supervisor Agent → [retry loop] → Output
```

**Agents:**
1. **Parsing** — extract text, technologies, projects, experience
2. **Context Extraction** — structured JSON context from JD + resume
3. **Question Generation** — 7 technical + 3 scenario questions
4. **Explanation** — concise recruiter-focused explanations
5. **Supervisor** — validates quality; triggers regeneration if needed

## Quick Start  

### Prerequisites

- Node.js 18+
- Python 3.11+
- [OpenRouter API key](https://openrouter.ai/)

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Set VITE_API_URL=http://localhost:8000

npm run dev
```

Open **http://localhost:5173**

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | Required — OpenRouter API key |
| `MODEL_PARSING` | Model for document parsing (default: Gemini Flash) |
| `MODEL_CONTEXT` | Model for context extraction |
| `MODEL_QUESTIONS` | Model for question generation |
| `MODEL_EXPLANATION` | Model for explanations |
| `MODEL_SUPERVISOR` | Model for quality validation |
| `FALLBACK_MODELS` | Comma-separated fallback models |
| `CORS_ORIGINS` | Allowed frontend origins |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/interview/upload/jd` | Upload job description |
| POST | `/api/interview/upload/resume` | Upload resume |
| POST | `/api/interview/generate` | Generate 10 questions |

## Deployment

### Backend (Render)

1. Create a new **Web Service** on Render
2. Set root directory to `backend`
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add env vars from `.env.example`
6. Set `CORS_ORIGINS` to your Vercel URL

Or use the included `render.yaml` blueprint.

### Frontend (Vercel)

1. Import the repo in Vercel
2. Set root directory to `frontend`
3. Framework preset: **Vite**
4. Add `VITE_API_URL` → your Render backend URL
5. Deploy

## Features

- Drag-and-drop upload (PDF, DOC, DOCX, TXT)
- File preview
- 10 contextual questions with difficulty & technology tags
- Copy question to clipboard
- Export questions to PDF
- Recruiter notes per question
- Dark / light mode
- Multi-agent LangGraph pipeline with supervisor retry loop

## Project Structure

```
AI_interview_platform/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph workflow & agent nodes
│   │   ├── api/routes/      # FastAPI routes
│   │   ├── core/            # Settings
│   │   ├── schemas/         # Pydantic models
│   │   └── services/        # OpenRouter, file parsing
│   ├── requirements.txt
│   └── render.yaml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── vercel.json
└── README.md
```

## License

MIT

# Deployment
