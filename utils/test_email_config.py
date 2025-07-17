#!/usr/bin/env python3
"""
Email Configuration Test for LCF Government Tracker
Tests email settings and identifies configuration issues.
"""

import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from JSON file."""
    try:
        with open("config.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found")
        return None
    except json.JSONDecodeError:
        logger.error("Invalid JSON in config.json")
        return None

def check_email_config(config):
    """Check if email configuration is complete."""
    logger.info("Checking email configuration...")
    
    required_fields = [
        "send_email",
        "email_from", 
        "email_to",
        "smtp_server",
        "smtp_port",
        "smtp_username",
        "smtp_password"
    ]
    
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in config:
            missing_fields.append(field)
        elif not config[field] or config[field] == "":
            empty_fields.append(field)
        elif field in ["email_from", "email_to", "smtp_username", "smtp_password"] and "example.com" in str(config[field]):
            empty_fields.append(f"{field} (still has example value)")
    
    # Check send_email specifically
    send_email = config.get("send_email", False)
    logger.info(f"send_email setting: {send_email}")
    
    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
    
    if empty_fields:
        logger.error(f"Empty or example values in fields: {empty_fields}")
    
    if not missing_fields and not empty_fields:
        logger.info("✓ All email configuration fields are present and filled")
        return True
    else:
        logger.error("✗ Email configuration is incomplete")
        return False

def test_smtp_connection(config):
    """Test SMTP connection without sending email."""
    logger.info("Testing SMTP connection...")
    
    try:
        smtp_server = config.get("smtp_server", "smtp.gmail.com")
        smtp_port = config.get("smtp_port", 587)
        smtp_username = config.get("smtp_username", "")
        smtp_password = config.get("smtp_password", "")
        use_tls = config.get("smtp_use_tls", True)
        
        logger.info(f"Connecting to {smtp_server}:{smtp_port}")
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            logger.info("Starting TLS...")
            server.starttls()
        
        if smtp_username and smtp_password:
            logger.info("Attempting login...")
            server.login(smtp_username, smtp_password)
            logger.info("✓ SMTP login successful")
        else:
            logger.warning("No username/password provided - skipping authentication")
        
        server.quit()
        logger.info("✓ SMTP connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"✗ SMTP connection failed: {e}")
        return False

def send_test_email(config):
    """Send a test email."""
    logger.info("Sending test email...")
    
    try:
        # Create test email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "LCF Government Tracker - Test Email"
        msg['From'] = config.get("email_from")
        msg['To'] = config.get("email_to")
        
        # Create test content
        text_content = """
This is a test email from your La Cañada Flintridge Government Tracker.

If you received this email, your email configuration is working correctly!

You can now run the full tracker system and receive weekly government updates.
"""
        
        html_content = """
<html>
<body>
<h2>LCF Government Tracker - Test Email</h2>
<p>This is a test email from your La Cañada Flintridge Government Tracker.</p>
<p><strong>If you received this email, your email configuration is working correctly!</strong></p>
<p>You can now run the full tracker system and receive weekly government updates.</p>
</body>
</html>
"""
        
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        smtp_server = config.get("smtp_server", "smtp.gmail.com")
        smtp_port = config.get("smtp_port", 587)
        smtp_username = config.get("smtp_username", "")
        smtp_password = config.get("smtp_password", "")
        use_tls = config.get("smtp_use_tls", True)
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            server.starttls()
        
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
        
        server.send_message(msg)
        server.quit()
        
        logger.info(f"✓ Test email sent successfully to {msg['To']}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to send test email: {e}")
        return False

def main():
    """Main test function."""
    print("="*60)
    print("LCF GOVERNMENT TRACKER - EMAIL CONFIGURATION TEST")
    print("="*60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Could not load configuration file")
        return False
    
    print(f"\n1. Configuration File Status: ✓ Loaded")
    
    # Check email configuration
    print(f"\n2. Email Configuration Check:")
    config_ok = check_email_config(config)
    
    if not config_ok:
        print("\n❌ Email configuration is incomplete. Please check the following:")
        print("   - Make sure all email fields are filled in config.json")
        print("   - Replace any 'example.com' values with your actual email settings")
        print("   - Ensure send_email is set to true")
        return False
    
    # Test SMTP connection
    print(f"\n3. SMTP Connection Test:")
    smtp_ok = test_smtp_connection(config)
    
    if not smtp_ok:
        print("\n❌ SMTP connection failed. Please check:")
        print("   - Your email server settings (smtp_server, smtp_port)")
        print("   - Your username and password")
        print("   - For Gmail: use an App Password, not your regular password")
        return False
    
    # Send test email
    print(f"\n4. Test Email Send:")
    email_ok = send_test_email(config)
    
    if email_ok:
        print("\n🎉 SUCCESS! Email configuration is working correctly.")
        print("   Check your inbox for the test email.")
        print("   Your LCF Government Tracker is ready to send weekly reports!")
    else:
        print("\n❌ Test email failed. Please check the error messages above.")
    
    print("\n" + "="*60)
    return email_ok

if __name__ == "__main__":
    main()

