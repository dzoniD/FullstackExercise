import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Učitaj environment varijable iz .env fajla
load_dotenv()

def send_verification_email(email: str, token: str):
    verify_link = f"{os.getenv('FRONTEND_URL')}/verify-email?token={token}"
    msg = EmailMessage()
    msg['Subject'] = "Verify your email"
    msg['From'] = os.getenv("SMTP_USER")
    msg['To'] = email

    msg.set_content(f"""
    Hi,

    Thanks for signing up 👋

    Please verify your account by clicking the link below:

    {verify_link}

    This link will expire in 30 minutes.

    If you didn't create an account, you can safely ignore this email.
    """)

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)

    return True