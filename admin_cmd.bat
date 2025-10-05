@echo off
REM Admin command script to add, commit, and push changes including email and mobile notification feature and fixes

git add .
git commit -m "Fix syntax error in app.py; add email and mobile notification feature; add .gitignore to exclude stray files"
git push origin main

echo Changes committed and pushed to GitHub successfully.
pause
