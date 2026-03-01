import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv(override=True)


def send_email(name, email, notes):
    msg = EmailMessage()
    msg["Subject"] = "Mail from Personal chat bot"
    msg["From"] = "siddardhavangala@gmail.com"
    msg["To"] = "siddardhavangala@gmail.com"

    msg.set_content(
        f"""
New interest recorded:

Name: {name}
Email: {email}
Notes: {notes}
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        msg.set_content(f"""New website interest received
                    Name: {name}
                    Email: {email}
                    Notes : {notes}
                    """
                    )
        server.send_message(msg)

if __name__ == "__main__":
    send_email("siddardha.vangala", "siddardhavangala@gmail.com", f"This is test email")
