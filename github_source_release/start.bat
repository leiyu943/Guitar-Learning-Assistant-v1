@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist "GuitarLearningAssistant\GuitarLearningAssistant.exe" (
  start "Guitar Learning Assistant" "GuitarLearningAssistant\GuitarLearningAssistant.exe"
) else (
  echo Executable not found. Please run: python main_window.py
  pause
)
