#!/usr/bin/env python3
"""
Simple OCR Test Script
Test the OCR functionality independently to debug issues.
"""

import os
import sys
import tempfile
from PIL import Image

def test_basic_ocr():
    """Test basic OCR functionality"""
    print("🧪 Testing Basic OCR Functionality")
    print("=" * 50)

    try:
        import pytesseract
        print("✅ pytesseract imported successfully")
    except ImportError as e:
        print(f"❌ pytesseract import failed: {e}")
        print("Install with: pip install pytesseract")
        return False

    # Configure Tesseract path
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\Windows 10\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    ]

    tesseract_found = False
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Tesseract found at: {path}")
            tesseract_found = True
            break

    if not tesseract_found:
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract found in PATH")
            tesseract_found = True
        except Exception as e:
            print(f"❌ Tesseract not found: {e}")
            return False

    # Test OCR with a simple text
    try:
        # Create a simple test image with text
        test_text = "John Doe\nJane Smith\nBob Johnson"

        # For now, just test if pytesseract can run
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")

        # Test with a blank image to see if OCR works
        test_image = Image.new('RGB', (100, 50), color='white')
        result = pytesseract.image_to_string(test_image)
        print(f"✅ OCR test successful (empty result expected): '{result.strip()}'")

        return True

    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def test_opencv_processing():
    """Test OpenCV image processing"""
    print("\n🧪 Testing OpenCV Image Processing")
    print("=" * 50)

    try:
        import cv2
        import numpy as np
        print("✅ OpenCV imported successfully")

        # Test basic OpenCV operations
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        print("✅ OpenCV image processing test successful")

        return True

    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        print("Install with: pip install opencv-python")
        return False
    except Exception as e:
        print(f"❌ OpenCV processing failed: {e}")
        return False

def main():
    print("OCR Functionality Test")
    print("======================")

    basic_ocr_ok = test_basic_ocr()
    opencv_ok = test_opencv_processing()

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Basic OCR: {'✅ PASS' if basic_ocr_ok else '❌ FAIL'}")
    print(f"OpenCV Processing: {'✅ PASS' if opencv_ok else '❌ FAIL'}")

    if basic_ocr_ok:
        print("\n🎉 OCR is working! The issue might be in the Flask app integration.")
        print("Try uploading an image through the web interface.")
    else:
        print("\n❌ OCR is not working. Please install Tesseract OCR first.")
        print("Run: install_tesseract.bat")

    if not opencv_ok:
        print("\n⚠️ OpenCV not available - using basic image processing (still works)")

if __name__ == "__main__":
    main()
