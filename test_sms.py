#!/usr/bin/env python3
"""
Test script for Email-to-SMS functionality
Run this to verify your SMS configuration is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_sms():
    """Test Email-to-SMS functionality"""
    print("🧪 Testing Email-to-SMS Configuration")
    print("=" * 50)

    # Check configuration
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    sms_gateway = os.getenv('SMS_GATEWAY', 'tmomail.net')
    sms_method = os.getenv('SMS_METHOD', 'console')

    print(f"📧 Email: {email_user}")
    print(f"🔑 Password: {'Set' if email_pass else 'Not set'}")
    print(f"📡 SMS Gateway: {sms_gateway}")
    print(f"📱 SMS Method: {sms_method}")
    print()

    if sms_method != 'email':
        print("⚠️  SMS_METHOD is not set to 'email'")
        print("   Please set SMS_METHOD=email in your .env file")
        return False

    if not email_user or not email_pass:
        print("❌ Email credentials not configured")
        print("   Please update EMAIL_USER and EMAIL_PASS in .env")
        return False

    # Test SMS sending
    try:
        import smtplib
        from email.mime.text import MIMEText

        # Test with your own phone number (replace with actual number)
        test_phone = input("Enter your phone number for testing (e.g., 1234567890): ").strip()
        if not test_phone:
            print("ℹ️  Skipping SMS test - no phone number provided")
            return True

        # Convert phone to email format
        sms_email = f"{test_phone}@{sms_gateway}"

        # Create test message
        test_message = "🎉 Test SMS from Attendance System!\nEmail-to-SMS is working perfectly! ✅"

        msg = MIMEText(test_message)
        msg['Subject'] = 'Attendance System Test'
        msg['From'] = email_user
        msg['To'] = sms_email

        print(f"📱 Sending test SMS to: {test_phone}")
        print(f"📧 Via email: {sms_email}")

        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.sendmail(email_user, sms_email, msg.as_string())
        server.quit()

        print("✅ Test SMS sent successfully!")
        print("📨 Check your Gmail sent folder")
        print("📱 Check your phone for the SMS message")
        return True

    except Exception as e:
        print(f"❌ SMS test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Verify your Gmail App Password is correct")
        print("2. Enable 'Less secure app access' in Gmail settings")
        print("3. Check your SMS gateway (tmomail.net for T-Mobile)")
        print("4. Make sure 2FA is enabled for App Password generation")
        return False

if __name__ == "__main__":
    success = test_email_sms()
    if success:
        print("\n🎉 Email-to-SMS is configured correctly!")
        print("🚀 Ready to send real attendance notifications")
    else:
        print("\n❌ Please fix the configuration and try again")
        sys.exit(1)
