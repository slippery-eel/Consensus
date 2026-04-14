@echo off
cd /d "%~dp0backend"
py -3.10 -m uvicorn app.main:app --reload --port 8000
