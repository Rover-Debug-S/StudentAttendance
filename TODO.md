# TODO: Implement Email and Mobile Notifications for Parents

## Steps to Complete

- [x] Add email column to User model in models.py
- [x] Update parent_register.html to include email input field
- [x] Update parent_register route in app.py to handle email during registration
- [x] Update API routes (api_parent_register, api_update_mobile) to include email
- [x] Rename update_mobile.html to update_contact.html and add email field
- [x] Modify send_sms_notification function to also send email notifications
- [x] Update notification sending logic to send to both email and mobile if available
- [x] Test parent registration with email
- [x] Test notification sending to both email and mobile
- [x] Handle database schema change (adding email column)
