@echo off
cd "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"

echo Setting up GitHub remote...
git remote set-url origin https://github.com/Rover-Debug-S/studentattendance.git

echo Cleaning stray files...
del /f /q "hing to GitHub..."
del /f /q "h origin HEAD"
del /f /q "h_github"
del /f /q "h"

echo Adding all changes...
git add .

echo.
echo Committing changes...
git commit -m "Replace app.py with fixed indentation and updated code"

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo Done! All changes have been pushed to GitHub.
pause
