@echo off
echo Creating pull request for OCR lazy loading changes...

REM Check if GitHub CLI is installed
gh --version >nul 2>&1
if %errorlevel% neq 0 (
    echo GitHub CLI not found. Installing...
    call install_gh.bat
)

REM Add and commit changes
git add app.py
git commit -m "Implement lazy loading for OCR reader in upload_attendance route

- Replace global OCR_READER usage with local ocr_reader variable
- Initialize OCR reader only when upload_attendance is accessed
- Improve error handling for OCR initialization failures
- Prevent Railway build timeouts by avoiding global OCR initialization"

REM Create and push branch
git checkout -b blackboxai/lazy-ocr-loading
git push --set-upstream origin blackboxai/lazy-ocr-loading

REM Create pull request
gh pr create --title "Implement lazy loading for OCR reader in upload_attendance route" --body "This PR replaces the global OCR_READER usage with a local ocr_reader variable in the upload_attendance route. It initializes the OCR reader only when the route is accessed, improving error handling and preventing build timeouts on Railway." --base main --head blackboxai/lazy-ocr-loading

echo Pull request created successfully!
pause
