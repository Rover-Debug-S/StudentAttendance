#!/usr/bin/env python3
"""
Simple test for Email-to-SMS functionality
"""

import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sms():
    """Test Email-to-SMS with hardcoded test values"""
    print("🧪 Testing Email-to-SMS Configuration")
    print("=" * 50)

    # Configuration
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    sms_gateway = os.getenv('SMS_GATEWAY', 'tmomail.net')

    print(f"📧 Email: {email_user}")
    print(f"🔑 Password: {'Set' if email_pass else 'Not set'}")
    print(f"📡 Gateway: {sms_gateway}")
    print()

    if not email_user or not email_pass:
        print("❌ Email credentials not configured")
        return False

    # Test SMS (using a test phone number - replace with real one)
    test_phone = "1234567890"  # Replace with your actual phone number
    sms_email = f"{test_phone}@{sms_gateway}"
    test_message = "🎉 Test SMS from Attendance System!\nEmail-to-SMS is working! ✅"

    try:
        print(f"📱 Sending test SMS to: {test_phone}")
        print(f"📧 Via: {sms_email}")

        # Create message
        msg = MIMEText(test_message)
        msg['Subject'] = 'Attendance System Test'
        msg['From'] = email_user
        msg['To'] = sms_email

        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.sendmail(email_user, sms_email, msg.as_string())
        server.quit()

        print("✅ Test SMS sent successfully!")
        print("📨 Check your Gmail sent folder")
        print("📱 Check your phone for the SMS")
        return True

    except Exception as e:
        print(f"❌ SMS test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Verify Gmail App Password")
        print("2. Check SMS gateway for your carrier")
        print("3. Enable 2FA for App Password")
        return False

if __name__ == "__main__":
    success = test_sms()
    if success:
        print("\n🎉 Email-to-SMS is working!")
    else:
        print("\n❌ Configuration needs fixing")
