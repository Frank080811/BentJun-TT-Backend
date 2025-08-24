from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from email.message import EmailMessage
import aiosmtplib

app = FastAPI(title="Contact Form API (Async Emails)")

# Allow frontend domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SMTP_EMAIL = "sarfof06@gmail.com"
SMTP_PASSWORD = "mhtehnhylovnlplj"
TO_EMAILS = ["bentjun25@gmail.com", "goddey1989@gmail.com"]
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

async def send_email_async(subject: str, body: str, to: list[str]):
    """Send email asynchronously using aiosmtplib."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = ", ".join(to)
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_EMAIL,
            password=SMTP_PASSWORD
        )
    except Exception as e:
        print("Email sending failed:", e)
        raise

@app.post("/send-contact")
async def send_contact(
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    message: str = Form(...)
):
    try:
        # Email to admin
        admin_subject = f"New Contact Form Submission from {name}"
        admin_body = f"""
You have a new contact form submission:

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}
"""
        # Email to client
        client_subject = "Thank you for contacting BentJun Hub"
        client_body = f"""
Hi {name},

Thank you for reaching out to BentJun Hub! We have received your message and one of our team members will contact you via phone at {phone} shortly.

Best regards,
BentJun Hub Team
"""
        # Send emails
        await send_email_async(admin_subject, admin_body, TO_EMAILS)
        await send_email_async(client_subject, client_body, [email])

        return {"status": "success", "message": "Contact form sent and acknowledgment email delivered."}

    except Exception as e:
        return {"status": "error", "message": str(e)}
