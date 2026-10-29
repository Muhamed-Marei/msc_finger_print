@echo off
title MSC Fingerprint System Launcher
echo ======================================================
echo Starting MSC Fingerprint Intelligence System...
echo ======================================================

start "MSC Backend (FastAPI :8000)" cmd /k ".\.venv\Scripts\uvicorn backend.api:app --reload --port 8000"

start "MSC Frontend (Next.js :3000)" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are launching in separate windows:
echo  - Backend API: http://127.0.0.1:8000
echo  - Frontend Web: http://localhost:3000
echo.
