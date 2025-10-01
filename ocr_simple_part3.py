def find_matching_students(ocr_text, all_students):
    """Find students whose names appear in the OCR text with detailed logging"""
    recognized_names = set()
    raw_text = ocr_text.lower()

    # Create student name dictionary
    student_names = {student.name.lower(): student for student in all_students}

    print("=== OCR Matching Debug ===")
    print(f"Total students to match: {len(student_names)}")

    # Split text into lines
    lines = ocr_text.split('\\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Clean the line (remove special characters except commas and periods)
        cleaned_line = ''.join(c for c in line if c.isalnum() or c.isspace() or c in [',', '.']).strip()

        print(f"Processing line: '{line}' -> cleaned: '{cleaned_line}'")

        # Check for exact matches and partial matches
        for student_name in student_names.keys():
            if student_name == cleaned_line.lower():
                recognized_names.add(student_name)
                print(f"Exact match found: {student_name}")
            elif student_name in cleaned_line.lower():
                recognized_names.add(student_name)
                print(f"Partial match found: {student_name}")

    # Also check the entire text
    for student_name in student_names.keys():
        if student_name in raw_text:
            recognized_names.add(student_name)
            print(f"Full text match found: {student_name}")

    print(f"Recognized names: {recognized_names}")

    # Get matched students
    matched_students = []
    detected_student_ids = []

    for student in all_students:
        if student.name.lower() in recognized_names:
            matched_students.append(student)
            detected_student_ids.append(student.id)

    print(f"Matched students count: {len(matched_students)}")

    return matched_students, detected_student_ids, recognized_names

def process_attendance_image(image_file, all_students):
    """Main function to process attendance image and return results with detailed logging"""
    try:
        # Save uploaded file temporarily
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            image_file.save(tmp.name)
            temp_path = tmp.name

        print(f"Saved uploaded image to temporary file: {temp_path}")

        # Extract text from image
        ocr_text = extract_text_from_image(temp_path)

        # Clean up temp file
        os.unlink(temp_path)
        print(f"Deleted temporary file: {temp_path}")

        if not ocr_text.strip():
            print("No text detected in image")
            return [], [], set(), "No text detected in image"

        # Find matching students
        matched_students, detected_ids, recognized_names = find_matching_students(ocr_text, all_students)

        return matched_students, detected_ids, recognized_names, None

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return [], [], set(), f"Error processing image: {str(e)}"

# Initialize Tesseract on import
TESSERACT_AVAILABLE = configure_tesseract()
