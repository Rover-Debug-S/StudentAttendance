@echo off
cd "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"

REM Thorough consolidate branches command
echo Performing thorough consolidation of all branches into main...

REM Fetch all remote branches
git fetch --all

REM Switch to main branch
git checkout main
git pull origin main

REM Get list of all local branches except main
for /f "tokens=*" %%i in ('git branch --list') do (
    set "branch=%%i"
    if not "!branch!"=="* main" if not "!branch!"=="  main" (
        echo Merging branch !branch! into main...
        git merge !branch! --no-ff -m "Merge branch !branch! into main"
        if !errorlevel! neq 0 (
            echo Conflict detected in merging !branch!. Attempting to resolve...
            git merge --abort
            echo Skipping !branch! due to conflicts. Please resolve manually.
        ) else (
            echo Deleting local branch !branch!...
            git branch -d !branch!
        )
    )
)

REM Delete all remote branches except main
for /f "tokens=*" %%i in ('git branch -r') do (
    set "remote_branch=%%i"
    echo !remote_branch! | findstr /C:"origin/main" >nul
    if !errorlevel! neq 0 (
        echo Deleting remote branch !remote_branch!...
        git push origin --delete !remote_branch!
    )
)

REM Push consolidated main branch
git push origin main --force
echo Thorough consolidation completed! All branches merged into main and cleaned up.

echo Done!
