#!/usr/bin/env python3
"""
Tesseract OCR Installation Checker
This script helps verify Tesseract installation and provides installation guidance.
"""

import os
import sys
import subprocess

def check_tesseract():
    """Check if Tesseract is installed and accessible"""
    print("🔍 Checking Tesseract OCR installation...")
    print("=" * 50)

    # Method 1: Try to run tesseract command
    try:
        result = subprocess.run(['tesseract', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Tesseract found in PATH!")
            print("Version info:")
            print(result.stdout)
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("❌ Tesseract not found in PATH")

    # Method 2: Check common installation paths
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.environ.get('USERNAME', 'User')),
        r'C:\Tesseract-OCR\tesseract.exe'
    ]

    print("\n🔍 Checking common installation paths...")
    found_paths = []

    for path in common_paths:
        if os.path.exists(path):
            found_paths.append(path)
            print(f"✅ Found Tesseract at: {path}")

    if found_paths:
        print(f"\n🎯 Found {len(found_paths)} Tesseract installation(s)")
        print("You can manually set the path in your Python code:")
        for path in found_paths:
            print(f"  pytesseract.pytesseract.tesseract_cmd = r'{path}'")
        return True

    return False

def install_instructions():
    """Provide installation instructions"""
    print("\n📋 INSTALLATION INSTRUCTIONS")
    print("=" * 50)
    print("1. Download Tesseract OCR from:")
    print("   https://github.com/UB-Mannheim/tesseract/wiki")
    print()
    print("2. Download the Windows installer:")
    print("   tesseract-ocr-w64-setup-v5.3.0.20221222.exe (or latest)")
    print()
    print("3. Run the installer as Administrator")
    print()
    print("4. Install to default location:")
    print("   C:\\Program Files\\Tesseract-OCR\\")
    print()
    print("5. IMPORTANT: Check 'Add to PATH' during installation")
    print()
    print("6. Restart your command prompt/terminal")
    print()
    print("7. Run this script again to verify installation")
    print()

def test_ocr():
    """Test OCR functionality with Python"""
    print("\n🧪 Testing OCR functionality...")
    try:
        import pytesseract
        from PIL import Image
        import tempfile

        # Create a simple test image (you would replace this with actual image)
        print("✅ pytesseract imported successfully")
        print("✅ PIL imported successfully")

        # Try to get version
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract version: {version}")
        except Exception as e:
            print(f"❌ Could not get version: {e}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required packages:")
        print("  pip install pytesseract pillow opencv-python")
        return False

def main():
    print("Tesseract OCR Installation Checker")
    print("==================================")

    # Check installation
    tesseract_found = check_tesseract()

    # Test Python integration
    python_ok = test_ocr()

    print("\n" + "=" * 50)
    if tesseract_found and python_ok:
        print("🎉 SUCCESS: Tesseract OCR is ready to use!")
        print("You can now use the OCR attendance marking feature.")
    else:
        print("❌ Tesseract OCR needs to be installed or configured.")
        install_instructions()

    print("\nNeed help? Check TESSERACT_INSTALL_GUIDE.md for detailed instructions.")
    print("=" * 50)

if __name__ == "__main__":
    main()
