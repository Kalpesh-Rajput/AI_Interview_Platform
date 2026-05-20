# AI Interview Platform - Production Deployment & CI/CD Guide

# Overview

This document explains the complete production deployment process for the AI Interview Platform using:

* Frontend → Vercel
* Backend → Render
* CI/CD → GitHub Actions
* Repository → GitHub

This setup provides:

* centralized CI/CD
* automated frontend deployment
* automated backend deployment
* production-grade deployment pipeline
* scalable SaaS architecture

---

# Production Architecture

```text id="m1x6rn"
Developer Pushes Code
        ↓
GitHub Repository
        ↓
GitHub Actions CI/CD
        ↓
-------------------------------------
|                                   |
Frontend Deployment            Backend Deployment
(Vercel)                       (Render)
|                                   |
React/Vite App                 FastAPI Backend
```

---

# Project Structure

```text id="wz9g9h"
project-root/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── .env
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── routers/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
│
└── .github/
    └── workflows/
        └── ci-cd.yml
```

---

# Backend Deployment - Render

# Step 1: Create Render Account

1. Open:
   https://render.com

2. Sign in using GitHub.

---

# Step 2: Create Web Service

1. Click:
   New → Web Service

2. Connect GitHub repository.

3. Select repository.

---

# Step 3: Configure Backend

Use the following settings:

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Runtime        | Python 3                                         |
| Root Directory | backend                                          |
| Build Command  | pip install -r requirements.txt                  |
| Start Command  | uvicorn app.main:app --host 0.0.0.0 --port 10000 |

---

# Step 4: Add Backend Environment Variables

Inside Render:

```text id="w0wzpb"
Service → Environment
```

Add all backend variables.

Example:

```env id="7xzjlwm"
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
JWT_SECRET=your_secret
DATABASE_URL=your_database_url
CORS_ORIGINS=https://your-frontend.vercel.app
```

---

# Step 5: Deploy Backend

Click:

```text id="2mq0tq"
Create Web Service
```

Render generates backend URL:

```text id="9qedyo"
https://your-backend.onrender.com
```

---

# Step 6: Test Backend

Open:

```text id="f1fd34"
https://your-backend.onrender.com/docs
```

If Swagger UI opens successfully, backend deployment is correct.

---

# Step 7: Generate Render Deploy Hook

Inside Render:

```text id="jv0j4r"
Service → Settings → Deploy Hook
```

Generate deploy hook.

Example:

```text id="c4f1v2"
https://api.render.com/deploy/srv-xxxxx?key=xxxxxxxx
```

IMPORTANT:
Store the FULL URL in GitHub Secrets.

NOT only:

```text id="3mkxg9"
srv-xxxxx
```

---

# Frontend Deployment - Vercel

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

```text id="0fl2zq"
Project → Settings → Environment Variables
```

Add:

```env id="3knb7l"
VITE_API_URL=https://your-backend.onrender.com
```

---

# Step 5: Deploy Frontend

Click:

```text id="y9jk9z"
Deploy
```

Vercel generates frontend URL:

```text id="z6ykx1"
https://your-frontend.vercel.app
```

---

# Frontend API Configuration

# Wrong Configuration

```javascript id="5lcjlwm"
baseURL: "http://localhost:8000"
```

This causes production CORS errors.

---

# Correct Configuration

```javascript id="6l18fb"
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 180000,
});

export default api;
```

---

# Backend CORS Configuration

# Render Environment Variable

```env id="35j11w"
CORS_ORIGINS=https://your-frontend.vercel.app
```

---

# FastAPI CORS Setup

```python id="ayr7c5"
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

# GitHub Actions CI/CD Setup

# Step 1: Create Workflow Folder

```text id="ifdrkm"
.github/workflows/
```

---

# Step 2: Create Workflow File

```text id="1q84uq"
.github/workflows/ci-cd.yml
```

---

# Final Production CI/CD Workflow

```yaml id="7lbjlwm"
name: Full Stack CI/CD

on:
  push:
    branches:
      - main

jobs:

  build-and-deploy:
    runs-on: ubuntu-latest

    steps:

    # =========================
    # Checkout Repository
    # =========================

    - name: Checkout Repo
      uses: actions/checkout@v4

    # =========================
    # FRONTEND DEPLOYMENT
    # =========================

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 18
        cache: npm
        cache-dependency-path: frontend/package-lock.json

    - name: Install Frontend Dependencies
      run: |
        cd frontend
        npm ci

    - name: Install Vercel CLI
      run: npm install --global vercel

    - name: Pull Vercel Environment
      run: |
        cd frontend
        vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

    - name: Build Frontend
      run: |
        cd frontend
        vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

    - name: Deploy Frontend to Vercel
      run: |
        cd frontend
        vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}

    # =========================
    # BACKEND DEPLOYMENT
    # =========================

    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
        cache: pip

    - name: Install Backend Dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Verify Backend Import
      env:
        CORS_ORIGINS: ${{ secrets.CORS_ORIGINS }}
      run: |
        cd backend
        python -c "import app.main; print('Backend imports successfully')"

    - name: Deploy Backend to Render
      run: |
        curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_URL }}
```

---

# GitHub Secrets Required

Inside GitHub Repository:

```text id="y8q2m9"
Settings → Secrets and Variables → Actions
```

Add:

| Secret Name            | Purpose                          |
| ---------------------- | -------------------------------- |
| VERCEL_TOKEN           | Vercel deployment authentication |
| VERCEL_ORG_ID          | Vercel organization ID           |
| VERCEL_PROJECT_ID      | Vercel project ID                |
| RENDER_DEPLOY_HOOK_URL | Full Render deploy hook URL      |
| CORS_ORIGINS           | Frontend production URL          |

---

# Getting Vercel Token

1. Open:
   https://vercel.com/account/tokens

2. Create token.

3. Copy token.

---

# Getting Vercel Org ID and Project ID

Run locally:

```bash id="rjlwmj"
cd frontend
vercel link
```

File created:

```text id="z5n5e2"
frontend/.vercel/project.json
```

Example:

```json id="dxndqg"
{
  "projectId": "prj_xxxxx",
  "orgId": "team_xxxxx"
}
```

Add these values to GitHub Secrets.

---

# Common Production Errors

# 1. Frontend Calling localhost

Problem:

```text id="vf0b0s"
http://localhost:8000
```

Fix:

```javascript id="h38af7"
import.meta.env.VITE_API_URL
```

---

# 2. CORS Error

Problem:

```text id="4mxq2n"
No 'Access-Control-Allow-Origin'
```

Fix:

```env id="jlwm1p"
CORS_ORIGINS=https://your-frontend.vercel.app
```

---

# 3. GitHub Actions Backend Validation Failure

Problem:

```text id="4s6c5n"
Field required: cors_origins
```

Fix:

```yaml id="67jlwm"
env:
  CORS_ORIGINS: ${{ secrets.CORS_ORIGINS }}
```

---

# 4. Render Deploy Hook Failure

Problem:

```text id="kswdv6"
curl: (6) Could not resolve host
```

Cause:
Only service ID stored instead of full deploy hook URL.

Wrong:

```text id="yq18gw"
srv-xxxxx
```

Correct:

```text id="hl0njh"
https://api.render.com/deploy/srv-xxxxx?key=xxxxxxxx
```

---

# 5. Vercel Deployment Failure

Cause:
Missing secrets.

Required:

* VERCEL_TOKEN
* VERCEL_ORG_ID
* VERCEL_PROJECT_ID

---

# Final Production Flow

```text id="shq2kp"
Developer Pushes Code
        ↓
GitHub Actions Triggered
        ↓
Frontend Build & Deploy
        ↓
Backend Validation
        ↓
Render Deploy Triggered
        ↓
Production Updated
```

---

# Security Recommendations

* Never expose API keys in frontend
* Use GitHub Secrets
* Restrict CORS origins
* Use HTTPS everywhere
* Rotate tokens periodically

---

# Future Scalability Improvements

Future production upgrades:

* Docker
* Kubernetes
* Redis caching
* PostgreSQL scaling
* Monitoring
* Logging
* Staging environment
* Blue/Green deployment
* Canary releases
* Load balancing
* CDN optimization

---

# Final Result

After setup:

```bash id="lsk0fv"
git push origin main
```

automatically:

* deploys frontend to Vercel
* deploys backend to Render
* validates backend
* updates production application
* runs centralized CI/CD pipeline

This creates a scalable enterprise-grade deployment architecture for the AI Interview Platform.
