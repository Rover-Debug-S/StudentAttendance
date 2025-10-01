#!/usr/bin/env python3
"""
Test real SMS functionality with user's phone number
"""
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def test_real_sms():
    """Test sending real SMS to user's phone number"""
    print("🧪 Testing Real SMS to Your Phone")
    print("=" * 50)

    # User's credentials
    EMAIL_USER = 'zidious57@gmail.com'
    EMAIL_PASS = 'wnaw mwrw bqxp sqcj'
    SMS_GATEWAY = 'smart.com.ph'

    # User's phone number
    user_phone = '09948154088'  # Your phone number

    print(f"📧 Email: {EMAIL_USER}")
    print(f"📱 Phone: {user_phone}")
    print(f"📡 Gateway: {SMS_GATEWAY}")
    print()

    # Test message
    test_message = f"🎉 Test SMS from Attendance System!\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nSMS is working! ✅"

    try:
        print(f"📤 Sending SMS to: {user_phone}")
        print(f"💬 Message: {test_message}")
        print()

        # Strip leading 0 from phone number for SMS gateway
        phone_number = user_phone.lstrip('0')

        # Convert phone to email format
        sms_email = f"{phone_number}@{SMS_GATEWAY}"

        print(f"📧 Converting to: {sms_email}")

        # Create message
        msg = MIMEText(test_message)
        msg['Subject'] = 'Attendance System Test'
        msg['From'] = EMAIL_USER
        msg['To'] = sms_email

        # Send email
        print("🔄 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("🔐 Logging in...")
        server.login(EMAIL_USER, EMAIL_PASS)
        print("📨 Sending email...")
        server.sendmail(EMAIL_USER, sms_email, msg.as_string())
        server.quit()

        print("\n✅ SUCCESS! SMS sent successfully!")
        print("📱 Check your phone for the SMS message")
        print("⏰ It may take 1-2 minutes to arrive")

        return True

    except Exception as e:
        print(f"\n❌ SMS failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check Gmail App Password is correct")
        print("2. Verify phone number format")
        print("3. Check SMS gateway for your carrier")
        print("4. Enable 2FA for Gmail App Password")
        print("5. Try different SMS gateway if needed")
        return False

if __name__ == '__main__':
    success = test_real_sms()
    if success:
        print("\n🎉 Real SMS test completed successfully!")
        print("📱 You should receive an SMS on your phone shortly")
    else:
        print("\n❌ SMS test failed - check configuration")
