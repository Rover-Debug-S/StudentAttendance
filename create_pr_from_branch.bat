@echo off
cd "C:\Users\Windows 10\Desktop\StudentAttendanceSystem"

echo Current branch:
git branch --show-current

echo.
echo This will create a pull request from the current branch to main.
echo Make sure you're on the feature branch you want to create a PR for.
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto :end

echo.
set /p title="Enter PR title: "
if "%title%"=="" (
    echo PR title cannot be empty.
    goto :end
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

:end
echo.
pause
