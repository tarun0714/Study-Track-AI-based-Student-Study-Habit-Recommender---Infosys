# backend/app/email_utils.py
import os
import smtplib
from email.mime.text import MIMEText

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")   # your email
EMAIL_PASS = os.getenv("EMAIL_PASS")   # app password (for Gmail etc)
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER or "")


def send_otp_email(to_email: str, otp_code: str, context: str = "login") -> None:
    """
    Sends a simple OTP email. Requires EMAIL_USER, EMAIL_PASS, EMAIL_HOST, EMAIL_PORT in .env
    """
    if not EMAIL_USER or not EMAIL_PASS:
        print("WARNING: EMAIL_USER or EMAIL_PASS not configured; skipping real email send.")
        print(f"OTP for {to_email} ({context}): {otp_code}")
        return

    subject = f"Your Study Insights OTP for {context.title()}"
    body = (
        f"Your one-time password (OTP) for {context} is: {otp_code}\n\n"
        "This code will expire in 10 minutes.\n\n"
        "If you didn't request this, you can ignore this email."
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
