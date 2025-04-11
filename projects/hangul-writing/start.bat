@echo off
setlocal enabledelayedexpansion

REM Check if .env file exists
if not exist .env (
  echo No .env file found. Creating example file...
  copy .env.example .env
  echo Please edit .env file with your API keys and run this script again.
  exit /b 1
)

REM Load environment variables from .env
for /F "tokens=1,2 delims==" %%A in (.env) do (
  set "%%A=%%B"
)

REM Check if required API keys are set
if "!IMGBB_API_KEY!"=="" (
  echo Error: IMGBB_API_KEY not found in .env file
  echo Please set IMGBB_API_KEY in your .env file
  exit /b 1
)

if "!HF_API_KEY!"=="" (
  echo Error: HF_API_KEY not found in .env file
  echo Please set HF_API_KEY in your .env file
  exit /b 1
)

REM Start the application with docker-compose
echo Starting Hangul Calligraphy Practice app with API-based inference...
docker-compose up