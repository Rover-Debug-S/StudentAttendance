#!/usr/bin/env python3
"""
Simple OCR Module for Attendance System
Basic implementation with detailed logging for debugging.
"""

import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import os
import tempfile

def configure_tesseract():
    """Configure Tesseract path for Windows"""
    try:
        # Try common installation paths
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\Windows 10\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        ]

        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Tesseract configured: {path}")
                return True

        # If not found in common paths, try to use from PATH
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract found in PATH")
            return True
        except Exception:
            print("❌ Tesseract not found")
            return False

    except Exception as e:
        print(f"❌ Tesseract configuration error: {e}")
        return False
