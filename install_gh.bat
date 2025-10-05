@echo off
echo Installing GitHub CLI...
winget install --id GitHub.cli --accept-source-agreements --accept-package-agreements
echo GitHub CLI installation complete.
echo Please authenticate with: gh auth login
pause
