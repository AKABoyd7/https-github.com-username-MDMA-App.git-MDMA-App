@echo off
echo =======================================
echo   MDMA AI Agent Startup
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Ollama is running
echo Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama might not be running
    echo Please make sure Ollama is installed and running
    echo Download from: https://ollama.ai
    echo Then run: ollama pull llama3
    echo.
    pause
)

REM Install dependencies if needed
echo Installing/Checking dependencies...
pip install -q langchain langgraph langchain-community

echo.
echo Starting AI Agent...
echo Type 'exit' or 'quit' to stop the agent
echo =======================================
echo.

python agent.py

pause
