from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from email.message import EmailMessage
import aiosmtplib

app = FastAPI(title="Travel & Tour API (Async Emails)")

# Allow frontend domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://travel-n-tour-frontend.onrender.com"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gmail SMTP settings
SMTP_EMAIL = "bentjuntravelandtour@gmail.com"
SMTP_PASSWORD = "tiqjkvmocgqldrjr"  # ✅ App Password
TO_EMAILS = ["bentjun25@gmail.com", "goddey1989@gmail.com"]
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


async def send_email_async(subject: str, body: str, to: list[str], attachments: list[UploadFile] = None):
    """Send email asynchronously using aiosmtplib (with optional attachments)."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = ", ".join(to)
    msg.set_content(body)

    # Attach files if provided
    if attachments:
        for file in attachments:
            try:
                content = await file.read()
                msg.add_attachment(
                    content,
                    maintype="application",
                    subtype="octet-stream",
                    filename=file.filename
                )
            except Exception as e:
                print(f"⚠️ Failed to attach {file.filename}: {e}")

    try:
        response = await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
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
    return {"status": "success", "message": "Travel & Tour API is live and running."}


@app.post("/send-contact")
async def send_contact(
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    inquiry: str = Form(...),
    message: str = Form(...),
):
    # Admin email
    admin_subject = f"New Contact Form Submission from {name} ({inquiry})"
    admin_body = f"""
You have a new contact form submission:

Name: {name}
Email: {email}
Phone: {phone}
Inquiry: {inquiry}

Message:
{message}
"""

    # Client email
    client_subject = "Thank you for contacting BentJun Hub"
    client_body = f"""
Hi {name},

Thank you for reaching out to BentJun Travel & Tour! 
We have received your {inquiry.lower()} inquiry and one of our team members will contact you via phone at {phone} shortly.

Best regards,  
BentJun Hub Team
"""

    admin_status = await send_email_async(admin_subject, admin_body, TO_EMAILS)
    client_status = await send_email_async(client_subject, client_body, [email])

    if admin_status is True and client_status is True:
        return {"status": "success", "message": "✅ Emails sent successfully."}
    else:
        return {"status": "error", "message": f"Admin: {admin_status}, Client: {client_status}"}
    client_body = f"""
Hi {name},

Thank you for reaching out to BentJun Travel & Tour! 
We have received your message and one of our team members will contact you via phone at {phone} shortly.

Best regards,  
BentJun Hub Team
"""

    admin_status = await send_email_async(admin_subject, admin_body, TO_EMAILS)
    client_status = await send_email_async(client_subject, client_body, [email])

    if admin_status is True and client_status is True:
        return {"status": "success", "message": "✅ Emails sent successfully."}
    else:
        return {"status": "error", "message": f"Admin: {admin_status}, Client: {client_status}"}


@app.post("/send-application")
async def send_application(
    fullName: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    destination: str = Form(...),
    travelDate: str = Form(...),
    returnDate: str = Form(None),
    passport: UploadFile = File(...),
    photo: UploadFile = File(...)
):
    # Admin email
    admin_subject = f"New VISA Application from {fullName}"
    admin_body = f"""
A new VISA application has been received:

Full Name: {fullName}
Email: {email}
Phone: {phone}
Destination: {destination}
Travel Date: {travelDate}
Return Date: {returnDate if returnDate else 'N/A'}

Attached documents: {passport.filename}, {photo.filename}
"""

    # Client acknowledgment email
    client_subject = "Your VISA Application Has Been Received"
    client_body = f"""
Hi {fullName},

Thank you for submitting your VISA application with BentJun Travel & Tour. 
We have received your details and attached documents. Our team will review your application and get back to you soon.

Best regards,  
BentJun Hub Team
"""

    # Send emails
    admin_status = await send_email_async(admin_subject, admin_body, TO_EMAILS, [passport, photo])
    client_status = await send_email_async(client_subject, client_body, [email])

    if admin_status is True and client_status is True:
        return {"status": "success", "message": "✅ Application and acknowledgment emails sent."}
    else:
        return {"status": "error", "message": f"Admin: {admin_status}, Client: {client_status}"}