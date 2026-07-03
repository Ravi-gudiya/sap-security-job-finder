@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python naukri_bot.py --run >> bot_run.log 2>&1
