#!/usr/bin/env bash
# SkillBridge single-service build for Render.
#
# Installs backend deps, builds the React SPA, and leaves `backend/` ready for
# uvicorn to serve both the API and frontend/dist from one process.
#
set -e

pip install -r backend/requirements.txt

cd frontend
npm ci
npm run build
cd ..
