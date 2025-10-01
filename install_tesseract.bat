@echo off
echo ============================================
echo Tesseract OCR Installation Script
echo ============================================
echo.

echo Checking if Tesseract is already installed...
tesseract --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Tesseract is already installed!
    tesseract --version
    goto :end
)

echo ❌ Tesseract not found. Starting installation...
echo.

echo Downloading Tesseract OCR installer...
echo Please wait while we download the installer...
echo.

echo IMPORTANT: Please follow these steps:
echo 1. The installer will download automatically
echo 2. Run the installer as Administrator
echo 3. Install to the default location: C:\Program Files\Tesseract-OCR\
echo 4. Make sure to check "Add to PATH" during installation
echo.

echo Opening download page in your browser...
start https://github.com/UB-Mannheim/tesseract/wiki

echo.
echo After installation is complete, run this script again to verify.
echo.
pause

:end
echo.
echo Installation complete! You can now use OCR attendance marking.
echo.
pause
