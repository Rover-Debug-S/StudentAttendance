@echo off
cd "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"
git status
git log --oneline -5
git branch -a
git ls-remote --heads origin
echo.
echo Press any key to exit...
pause >nul
