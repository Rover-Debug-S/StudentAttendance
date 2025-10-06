@echo off
REM Admin command script to add, commit, and push changes including email and mobile notification feature, fixes, and parent_register route addition

cd "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"
git config --global --add safe.directory "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"
git add .
git commit -m "Fix syntax error in app.py; add email and mobile notification feature; add .gitignore; add parent_register route"
git push origin main

echo Changes committed and pushed to GitHub successfully.
pause
