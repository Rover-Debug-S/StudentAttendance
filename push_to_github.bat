@echo off
REM This script stages all changes, commits with a message, and pushes to the current branch on origin.

set /p commit_message=Enter commit message: 

git add .
git commit -m "%commit_message%"
git push origin HEAD

echo Done!
