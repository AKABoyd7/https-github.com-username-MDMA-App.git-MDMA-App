@echo off
REM Jareth2 Autonomous AI Agent Launcher
REM Copyright (c) 2025 AlphaEdge AINV. All rights reserved.

cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" "%~dp0jareth2_agent.py" %*
