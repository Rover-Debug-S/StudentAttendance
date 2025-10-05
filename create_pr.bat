@echo off
cd "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"
gh pr create --title "Fix Railway deployment issues" --body "Disable Tesseract on Railway and fix database queries to avoid internal server errors" --base main --head blackboxai/add-email-support
echo Pull request created successfully.
pause
