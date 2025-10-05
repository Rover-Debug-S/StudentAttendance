@echo off
cd "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"

echo ========================================
echo    STUDENT ATTENDANCE SYSTEM ADMIN CMD
echo ========================================
echo.
echo Choose an option:
echo 1. Consolidate all branches into main
echo 2. Create pull request from current branch
echo 3. Check git status
echo 4. Push current branch
echo 5. Push to GitHub (commit and push)
echo 6. Exit
echo.

:menu
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto consolidate
if "%choice%"=="2" goto create_pr
if "%choice%"=="3" goto status
if "%choice%"=="4" goto push
if "%choice%"=="5" goto push_github
if "%choice%"=="6" goto exit

echo Invalid choice. Please try again.
goto menu

:consolidate
echo.
echo Performing thorough consolidation of all branches into main...
echo.

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
echo.
echo Thorough consolidation completed! All branches merged into main and cleaned up.
goto menu

:create_pr
echo.
echo Current branch:
git branch --show-current
echo.
echo This will create a pull request from the current branch to main.
echo Make sure you're on the feature branch you want to create a PR for.
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto menu

echo.
set /p title="Enter PR title: "
if "%title%"=="" (
    echo PR title cannot be empty.
    goto menu
)

echo.
set /p body="Enter PR description (optional): "

echo.
echo Creating pull request...
gh pr create --title "%title%" --body "%body%" --base main

if %errorlevel% equ 0 (
    echo.
    echo Pull request created successfully!
) else (
    echo.
    echo Failed to create pull request. Check the error above.
)
goto menu

:status
echo.
echo Git Status:
git status
echo.
echo Recent commits:
git log --oneline -5
goto menu

:push
echo.
echo Current branch:
git branch --show-current
echo.
set /p confirm="Push current branch to remote? (y/n): "
if /i "%confirm%"=="y" (
    git push origin HEAD
    echo Branch pushed successfully!
)
goto menu

:push_github
echo.
echo Current branch:
git branch --show-current
echo.
echo This will add all changes, commit them, and push to GitHub.
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto menu

echo.
set /p commit_msg="Enter commit message: "
if "%commit_msg%"=="" (
    echo Commit message cannot be empty.
    goto menu
)

echo.
echo Adding all changes...
git add .

echo.
echo Committing changes...
git commit -m "%commit_msg%"

if %errorlevel% equ 0 (
    echo.
    echo Pushing to GitHub...
    git push origin HEAD
    if %errorlevel% equ 0 (
        echo.
        echo Successfully pushed to GitHub!
    ) else (
        echo.
        echo Failed to push to GitHub. Check the error above.
    )
) else (
    echo.
    echo No changes to commit or commit failed.
)
goto menu

:exit
echo.
echo Goodbye!
pause
