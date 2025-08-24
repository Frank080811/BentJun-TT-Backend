from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from email.message import EmailMessage
import aiosmtplib

app = FastAPI(title="Contact Form API (Async Emails)")

# Allow frontend domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://travel-n-tour-frontend.onrender.com"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gmail SMTP settings
SMTP_EMAIL = "sarfof06@gmail.com"
SMTP_PASSWORD = "hdexevxgafwyvcwb"  # ✅ Correct App Password
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
        response = await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,  # Gmail requires STARTTLS on port 587
            username=SMTP_EMAIL,
            password=SMTP_PASSWORD,
        )
        print(f"✅ Email sent to {to}: {response}")
        return True
    except aiosmtplib.errors.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed. Check your App Password.")
        return "SMTP Authentication failed"
    except Exception as e:
        print(f"❌ Email sending failed to {to}: {e}")
        return str(e)


@app.get("/")
async def root():
    """Root endpoint to confirm API is running"""
    return {"status": "success", "message": "Contact API is live and running."}


@app.post("/send-contact")
async def send_contact(
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    message: str = Form(...),
):
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

Thank you for reaching out to BentJun Travel & Tour! We have received your message and one of our team members will contact you via phone at {phone} shortly.

Best regards,
BentJun Hub Team
"""

    # Send both emails asynchronously
    admin_status = await send_email_async(admin_subject, admin_body, TO_EMAILS)
    client_status = await send_email_async(client_subject, client_body, [email])

    # Respond to frontend
    if admin_status is True and client_status is True:
        return {"status": "success", "message": "✅ Emails sent successfully."}
    else:
        return {
            "status": "error",
            "message": f"Admin email: {admin_status}, Client email: {client_status}",
        }
