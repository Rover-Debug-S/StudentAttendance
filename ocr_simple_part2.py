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
    """Extract text from image using basic OCR with detailed logging"""
    try:
        # Open image
        image = Image.open(image_path)

        # Preprocess image
        processed_image = preprocess_image_basic(image)

        # OCR configuration for better text recognition
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789., '

        # Extract text
        text = pytesseract.image_to_string(processed_image, config=custom_config)

        # Debug: print extracted text and save processed image for inspection
        print("=== OCR Extracted Text ===")
        print(text)
        print("==========================")

        # Save processed image for debugging
        debug_image_path = image_path + "_processed_debug.png"
        processed_image.save(debug_image_path)
        print(f"Processed image saved for debugging: {debug_image_path}")

        return text

    except Exception as e:
        print(f"❌ OCR extraction failed: {e}")
        return ""
