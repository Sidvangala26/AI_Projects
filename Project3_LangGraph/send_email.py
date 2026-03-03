import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv(override=True)


def send_email_from_llm(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "siddardhavangala@gmail.com"
    msg["To"] = "siddardhavangala@outlook.com"


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        msg.set_content(body)
        server.send_message(msg)

if __name__ == "__main__":
    send_email_from_llm("siddardha.vangala", "siddardhavangala@gmail.com", f"This is test email")
