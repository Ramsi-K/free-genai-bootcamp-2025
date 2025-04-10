@echo off
echo ================================== 
echo Korean Handwriting Practice Startup
echo ==================================

REM Check for Docker
where docker >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo X Docker not found. Please install Docker first.
    exit /b 1
)

echo Starting containers...
docker-compose up -d

echo Waiting for Ollama service to be ready...
set MAX_RETRIES=30
set count=0

:WAIT_LOOP
if %count% geq %MAX_RETRIES% (
    echo X Ollama did not start properly. Check docker logs with 'docker-compose logs ollama'
    exit /b 1
)

curl -s --fail http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✓ Ollama is ready!
    goto :OLLAMA_READY
)

echo Still waiting for Ollama to start... (%count%/%MAX_RETRIES%)
timeout /t 2 /nobreak >nul
set /a count+=1
goto :WAIT_LOOP

:OLLAMA_READY
echo Pulling Korean LLM model (this may take a while)...
curl -X POST http://localhost:11434/api/pull -d "{\"name\": \"kimjk/llama3.2-korean\"}"

echo.
echo ✨ Setup complete! The app is running at http://localhost:5000
echo 💡 Press Ctrl+C to stop watching logs
echo 📝 Use 'docker-compose down' when you want to shut down the app
echo.

REM Show logs
docker-compose logs -f web