from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import smtplib
from email.message import EmailMessage

app = FastAPI(title="Contact Form API")

# Allow CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for validation
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: str
    message: str

SMTP_EMAIL = "sarfof06@gmail.com"
SMTP_PASSWORD = "mhtehnhylovnlplj"
TO_EMAILS = ["bentjun25@gmail.com", "piesiegloria25@gmail.com"]

def send_email(subject: str, body: str, to: list):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SMTP_EMAIL
    msg['To'] = ", ".join(to)
    msg.set_content(body)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)

@app.post("/send-contact")
async def send_contact(
    name: str = Form(...),
    email: str = Form(...),
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
        send_email(admin_subject, admin_body, TO_EMAILS)

        # Automated acknowledgment to client
        client_subject = "Thank you for contacting BentJun Hub"
        client_body = f"""
Hi {name},

Thank you for reaching out to BentJun Hub! We have received your message and one of our team members will contact you via phone at {phone} shortly.

Best regards,
BentJun Hub Team
"""
        send_email(client_subject, client_body, [email])

        return {"status": "success", "message": "Contact form sent and acknowledgment email delivered."}

    except Exception as e:
        return {"status": "error", "message": str(e)}
