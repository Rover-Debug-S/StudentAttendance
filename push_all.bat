@echo off
cd "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"

echo Adding all changes...
git add .

echo.
echo Committing changes...
git commit -m "Add test notification after parent registration to verify contact info"

echo.
echo Pushing to GitHub...
git push origin HEAD

echo.
echo Done! All changes have been pushed to GitHub.
pause
