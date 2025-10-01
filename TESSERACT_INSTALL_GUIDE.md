# Tesseract OCR Installation Guide for Windows

## Step 1: Download Tesseract
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest version (tesseract-ocr-w64-setup-v5.3.0.20221222.exe or similar)
3. Run the installer as Administrator
4. Install to default location: `C:\Program Files\Tesseract-OCR\`

## Step 2: Add to PATH
1. Right-click "This PC" → Properties → Advanced system settings
2. Click "Environment Variables"
3. Under "System variables", find "Path" and click "Edit"
4. Click "New" and add: `C:\Program Files\Tesseract-OCR\`
5. Click "OK" on all windows

## Step 3: Verify Installation
1. Open Command Prompt
2. Type: `tesseract --version`
3. You should see version information

## Step 4: Test with Python
```python
import pytesseract
print(pytesseract.get_tesseract_version())
```

## Alternative: Chocolatey Installation
If you have Chocolatey installed:
```cmd
choco install tesseract
```

## Troubleshooting
- If still getting errors, the path might be different
- Check where Tesseract was actually installed
- Update the path in your Python code if needed:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
