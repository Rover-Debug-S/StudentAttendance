#!/usr/bin/env python3
"""
Simple OCR Module for Attendance System
Basic implementation without complex dependencies.
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

def preprocess_image_basic(image):
    """Basic image preprocessing using PIL only"""
    try:
        # Convert to grayscale
        gray = image.convert('L')

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2.0)

        # Apply slight blur to reduce noise
        filtered = enhanced.filter(ImageFilter.MedianFilter(size=3))

        # Simple thresholding
        threshold = filtered.point(lambda x: 0 if x < 128 else 255, '1')

        return threshold

    except Exception as e:
        print(f"❌ Image preprocessing failed: {e}")
        return image.convert('L')

def extract_text_from_image(image_path):
    """Extract text from image using basic OCR"""
    try:
        # Open image
        image = Image.open(image_path)

        # Preprocess image
        processed_image = preprocess_image_basic(image)

        # OCR configuration for better text recognition
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789. '

        # Extract text
        text = pytesseract.image_to_string(processed_image, config=custom_config)

        return text

    except Exception as e:
        print(f"❌ OCR extraction failed: {e}")
        return ""

def find_matching_students(ocr_text, all_students):
    """Find students whose names appear in the OCR text"""
    recognized_names = set()
    raw_text = ocr_text.lower()

    # Create student name dictionary
    student_names = {student.name.lower(): student for student in all_students}

    # Split text into lines
    lines = ocr_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Clean the line (remove special characters)
        cleaned_line = ''.join(c for c in line if c.isalnum() or c.isspace()).strip()

        # Check for exact matches
        for student_name in student_names.keys():
            if student_name == cleaned_line.lower():
                recognized_names.add(student_name)
            elif student_name in cleaned_line.lower():
                recognized_names.add(student_name)

    # Also check the entire text
    for student_name in student_names.keys():
        if student_name in raw_text:
            recognized_names.add(student_name)

    # Get matched students
    matched_students = []
    detected_student_ids = []

    for student in all_students:
        if student.name.lower() in recognized_names:
            matched_students.append(student)
            detected_student_ids.append(student.id)

    return matched_students, detected_student_ids, recognized_names

def process_attendance_image(image_file, all_students):
    """Main function to process attendance image and return results"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            image_file.save(tmp.name)
            temp_path = tmp.name

        # Extract text from image
        ocr_text = extract_text_from_image(temp_path)

        # Clean up temp file
        os.unlink(temp_path)

        if not ocr_text.strip():
            return [], [], set(), "No text detected in image"

        # Find matching students
        matched_students, detected_ids, recognized_names = find_matching_students(ocr_text, all_students)

        return matched_students, detected_ids, recognized_names, None

    except Exception as e:
        return [], [], set(), f"Error processing image: {str(e)}"

# Initialize Tesseract on import
TESSERACT_AVAILABLE = configure_tesseract()
