#!/usr/bin/env python3
"""
Send SMS to user's phone number: 09948154088
"""
import os
import smtplib
from email.mime.text import MIMEText

# SMS Configuration
EMAIL_USER = 'zidious57@gmail.com'
EMAIL_PASS = 'wnaw mwrw bqxp sqcj'
SMS_GATEWAY = 'smart.com.ph'
USER_PHONE = '09948154088'

def send_sms_to_user(phone_number, message):
    """Send SMS to user's phone number"""
    try:
        # Strip leading 0 from phone number for SMS gateway
        phone_number = phone_number.lstrip('0')

        # Convert phone to email format (e.g., 9948154088@smart.com.ph)
        sms_email = f"{phone_number}@{SMS_GATEWAY}"

        msg = MIMEText(message)
        msg['Subject'] = 'Student Attendance System Test'
        msg['From'] = EMAIL_USER
        msg['To'] = sms_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, sms_email, msg.as_string())
        server.quit()

        print(f"✅ SMS sent successfully to {phone_number}")
        print(f"📧 Email sent to: {sms_email}")
        print(f"📱 Message: {message}")
        return True
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False

def main():
    print("📱 Sending SMS to user's phone number...")
    print(f"📞 Phone: {USER_PHONE}")
    print(f"🌐 Gateway: {SMS_GATEWAY}")
    print()

    message = "Hello! This is a test SMS from your Student Attendance System. The system is working correctly! 🎓📚"

    success = send_sms_to_user(USER_PHONE, message)

    if success:
        print("\n🎉 SMS sent successfully!")
        print("📱 Check your phone for the message.")
    else:
        print("\n❌ Failed to send SMS.")
        print("🔧 Check your email credentials and SMS gateway settings.")

if __name__ == '__main__':
    main()
