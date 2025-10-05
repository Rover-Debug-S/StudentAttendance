@echo off
REM Admin command script to add, commit, and push changes including email and mobile notification feature and fixes

git add .
git commit -m "Add email and mobile notification feature for parents; fix syntax error in app.py; add .gitignore to exclude stray files"
git push origin main

echo Changes pushed to GitHub successfully.
pause
