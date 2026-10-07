@echo off
title Setup - AI Resume Analyzer & Job Matcher
echo ===================================================
echo   Installing Dependencies and Setting Up AI Model
echo ===================================================
echo.
cd /d "%~dp0"
pip install -r requirements.txt
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab')"
python assets/sample_resumes/create_samples.py
python build_project.py
echo.
echo ===================================================
echo   Setup Complete! Run run.bat to launch the app.
echo ===================================================
pause
