@echo off
title AI Resume Analyzer & Job Matcher
echo ===================================================
echo   Starting AI Resume Analyzer & Job Matcher...
echo ===================================================
echo.
cd /d "%~dp0"
streamlit run app.py
pause
