@echo off
echo Consolidating all branches into main...

REM Switch to main branch
git checkout main

REM Get list of all branches except main
for /f "tokens=*" %%i in ('git branch --list') do (
    set "branch=%%i"
    if not "!branch!"=="* main" if not "!branch!"=="  main" (
        echo Merging branch !branch! into main...
        git merge !branch!
        echo Deleting branch !branch!...
        git branch -d !branch!
    )
)

REM Push consolidated main branch
git push origin main --force

echo All branches consolidated into main successfully!
pause
