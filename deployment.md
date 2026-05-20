# AI Interview Platform - Production Deployment Guide

# Overview

This document explains the complete production deployment process for the AI Interview Platform using:

* Frontend → Vercel
* Backend → Render
* CI/CD → GitHub Actions
* Repository → GitHub

---

# Architecture

```text
GitHub Repository
        ↓
GitHub Actions CI/CD
        ↓
--------------------------------
|                              |
Frontend → Vercel             Backend → Render
|                              |
React/Vite App                FastAPI Backend
```

---

# Project Structure

```text
project-root/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env
│
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
│
└── .github/
    └── workflows/
        └── ci-cd.yml
```

---

# Backend Deployment (Render)

# Step 1: Create Render Account

1. Open:
   https://render.com

2. Sign in using GitHub.

---

# Step 2: Create Web Service

1. Click:
   New → Web Service

2. Select GitHub repository.

---

# Step 3: Configure Backend

Use these settings:

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Runtime        | Python 3                                         |
| Root Directory | backend                                          |
| Build Command  | pip install -r requirements.txt                  |
| Start Command  | uvicorn app.main:app --host 0.0.0.0 --port 10000 |

---

# Step 4: Add Environment Variables

Add all backend secrets inside:

Render Dashboard → Environment Variables

Example:

```env
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
JWT_SECRET=your_secret
DATABASE_URL=your_db_url
CORS_ORIGINS=https://your-frontend.vercel.app
```

---

# Step 5: Deploy Backend

Click:

```text
Create Web Service
```

Render will generate a backend URL:

```text
https://your-backend.onrender.com
```

---

# Step 6: Test Backend

Open:

```text
https://your-backend.onrender.com/docs
```

If Swagger UI opens successfully, backend deployment is working.

---

# Frontend Deployment (Vercel)

# Step 1: Create Vercel Account

1. Open:
   https://vercel.com

2. Sign in using GitHub.

---

# Step 2: Create Frontend Project

1. Click:
   Add New → Project

2. Import GitHub repository.

---

# Step 3: Configure Frontend

If frontend exists inside frontend/ folder:

| Field                   | Value         |
| ----------------------- | ------------- |
| Root Directory          | frontend      |
| Build Command           | npm run build |
| Install Command         | npm install   |
| Output Directory (Vite) | dist          |

---

# Step 4: Add Frontend Environment Variables

Inside Vercel:

Settings → Environment Variables

Add:

```env
VITE_API_URL=https://your-backend.onrender.com
```

---

# Step 5: Deploy Frontend

Click:

```text
Deploy
```

Vercel will generate frontend URL:

```text
https://your-frontend.vercel.app
```

---

# Backend CORS Configuration

Update Render Environment Variable:

```env
CORS_ORIGINS=https://your-frontend.vercel.app
```

---

# FastAPI CORS Setup

Inside backend:

```python
from fastapi.middleware.cors import CORSMiddleware
import os

origins = [os.getenv("CORS_ORIGINS")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# Frontend API Configuration

Correct frontend axios configuration:

```javascript
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 180000,
});

export default api;
```

---

# GitHub Actions CI/CD Setup

# Step 1: Create Workflow Folder

```text
.github/workflows/
```

---

# Step 2: Create Workflow File

File:

```text
.github/workflows/ci-cd.yml
```

---

# Production CI/CD Workflow

```yaml
name: Production CI/CD

on:
  push:
    branches:
      - main

jobs:

  deploy:
    runs-on: ubuntu-latest

    steps:

      - name: Checkout Repository
        uses: actions/checkout@v4

      # =========================
      # FRONTEND
      # =========================

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install Frontend Dependencies
        working-directory: frontend
        run: npm ci

      - name: Install Vercel CLI
        run: npm install --global vercel

      - name: Pull Vercel Environment
        working-directory: frontend
        run: |
          vercel pull --yes \
          --environment=production \
          --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build Frontend
        working-directory: frontend
        run: |
          vercel build --prod \
          --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy Frontend
        working-directory: frontend
        run: |
          vercel deploy --prebuilt --prod \
          --token=${{ secrets.VERCEL_TOKEN }}

      # =========================
      # BACKEND
      # =========================

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Backend Dependencies
        working-directory: backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Verify Backend
        working-directory: backend
        run: |
          python -c "import app.main; print('Backend imports successfully')"

      - name: Deploy Backend to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_URL }}
```

---

# GitHub Secrets Required

Inside GitHub Repository:

Settings → Secrets and Variables → Actions

Add:

| Secret Name            | Purpose                          |
| ---------------------- | -------------------------------- |
| VERCEL_TOKEN           | Vercel deployment authentication |
| VERCEL_ORG_ID          | Vercel organization ID           |
| VERCEL_PROJECT_ID      | Vercel project ID                |
| RENDER_DEPLOY_HOOK_URL | Render deploy hook URL           |

---

# Getting Vercel Token

1. Open:
   https://vercel.com/account/tokens

2. Create token.

3. Copy token.

---

# Getting Vercel Org ID and Project ID

Run locally:

```bash
cd frontend
vercel link
```

File created:

```text
frontend/.vercel/project.json
```

Example:

```json
{
  "projectId": "prj_xxxxx",
  "orgId": "team_xxxxx"
}
```

---

# Getting Render Deploy Hook

Inside Render:

```text
Service → Settings → Deploy Hook
```

Generate hook.

Example:

```text
https://api.render.com/deploy/srv-xxxxx?key=xxxxx
```

---

# Production Deployment Flow

```text
Developer Pushes Code
        ↓
GitHub Actions Triggered
        ↓
Frontend Build & Deploy (Vercel)
        ↓
Backend Validation
        ↓
Render Deployment Triggered
        ↓
Production Updated
```

---

# Common Production Errors

# 1. CORS Error

Cause:

* frontend URL not added in backend CORS

Fix:

```env
CORS_ORIGINS=https://your-frontend.vercel.app
```

---

# 2. Frontend Calling localhost

Wrong:

```javascript
http://localhost:8000
```

Correct:

```javascript
import.meta.env.VITE_API_URL
```

---

# 3. Render Build Failure

Cause:

* missing dependencies

Fix:

* ensure requirements.txt contains all packages

---

# 4. Vercel Deployment Failure

Cause:

* missing Vercel secrets

Fix:

* add:

  * VERCEL_TOKEN
  * VERCEL_ORG_ID
  * VERCEL_PROJECT_ID

---

# Production Recommendations

# Security

* Never expose API keys in frontend
* Use environment variables
* Restrict CORS origins
* Rotate secrets regularly

---

# Scalability

Future improvements:

* Docker
* Kubernetes
* Redis caching
* PostgreSQL
* Monitoring
* Logging
* Staging environment
* Blue/Green deployment
* Load balancing

---

# Final Result

After setup:

```text
git push origin main
```

automatically:

* deploys frontend
* deploys backend
* updates production application
* runs through centralized CI/CD

This creates a production-grade deployment architecture suitable for enterprise SaaS applications.
