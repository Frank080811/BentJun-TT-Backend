#app.py

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from dotenv import load_dotenv
import os
import base64
import shutil


# ==============================================================
# 🚀 FastAPI App Setup
# ==============================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.travelabroad.bentjun.com", 
        "https://travelabroad.bentjun.com",    
        "http://localhost:3033",
        "http://127.0.0.1:3033"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

# ==============================================================
# ✉️ Email Configuration
# ==============================================================

# Load environment variables from .env file
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
TO_EMAILS = [ADMIN_EMAIL]

sg_client = SendGridAPIClient(SENDGRID_API_KEY)



# ==============================================================
# 📩 Email Utility Function
# ==============================================================

async def send_email_async(subject: str, body: str, to: list[str], attachments: list = None):
    """Send email asynchronously using SendGrid API (supports attachments)."""
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to,
            subject=subject,
            html_content=body,
        )

        # Add attachments if any
        if attachments:
            for file in attachments:
                try:
                    if hasattr(file, "read"):  # FastAPI UploadFile
                        content = await file.read()
                        filename = file.filename
                    else:  # path
                        with open(file, "rb") as f:
                            content = f.read()
                        filename = os.path.basename(file)

                    encoded = base64.b64encode(content).decode()
                    attached_file = Attachment(
                        FileContent(encoded),
                        FileName(filename),
                        FileType("application/octet-stream"),
                        Disposition("attachment"),
                    )
                    message.add_attachment(attached_file)
                except Exception as e:
                    print(f"⚠️ Could not attach file {file}: {e}")

        response = sg_client.send(message)
        print(f"✅ Email sent to {to}. Status: {response.status_code}")
        return True

    except Exception as e:
        print(f"❌ Email failed to {to}: {e}")
        return str(e)


# ==============================================================
# 🏠 Root Endpoint
# ==============================================================

@app.get("/")
async def root():
    return {"status": "success", "message": "BentJun Travel & Tour API is live and running."}


# ==============================================================
# 📞 Contact Form Endpoint
# ==============================================================

@app.post("/send-contact")
async def send_contact(
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    inquiry: str = Form(...),
    message: str = Form(...),
):
    admin_subject = f"New Contact Form Submission from {name} ({inquiry})"
    admin_body = f"""
    <h2>📩 New Contact Form Submission</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Phone:</strong> {phone}</p>
    <p><strong>Inquiry Type:</strong> {inquiry}</p>
    <p><strong>Message:</strong></p>
    <p>{message}</p>
    """

    client_subject = "Thank You for Contacting BentJun Hub"
    client_body = f"""
    <p>Hi {name},</p>
    <p>Thank you for reaching out to <strong>BentJun Travel & Tour</strong>!</p>
    <p>We’ve received your inquiry and one of our team members will contact you shortly.</p>
    <p>Best regards,<br><strong>BentJun Hub Team</strong></p>
    """

    admin_status = await send_email_async(admin_subject, admin_body, TO_EMAILS)
    client_status = await send_email_async(client_subject, client_body, [email])

    if admin_status is True and client_status is True:
        return {"status": "success", "message": "✅ Emails sent successfully."}
    else:
        return {"status": "error", "message": f"Admin: {admin_status}, Client: {client_status}"}


# ==============================================================
# 🧳 Visa Application Endpoint
# ==============================================================

@app.post("/send-application")
async def send_application(
    fullName: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    pob: str = Form(...),
    ms: str = Form(...),
    occupation: str = Form(...),
    address: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    passport: UploadFile = File(...),
    photo: UploadFile = File(...),
):
    """Handle full Visa Application Form submission."""

    passport_path = os.path.join("uploads", passport.filename)
    photo_path = os.path.join("uploads", photo.filename)
    with open(passport_path, "wb") as f:
        shutil.copyfileobj(passport.file, f)
    with open(photo_path, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    admin_subject = f"🧳 New VISA Application from {fullName}"
    admin_body = f"""
    <h2>New VISA Application Received</h2>
    <p><strong>Full Name:</strong> {fullName}</p>
    <p><strong>Date of Birth:</strong> {dob}</p>
    <p><strong>Gender:</strong> {gender}</p>
    <p><strong>Nationality:</strong> {nationality}</p>
    <p><strong>Place of Birth:</strong> {pob}</p>
    <p><strong>Marital Status:</strong> {ms}</p>
    <p><strong>Occupation:</strong> {occupation}</p>
    <p><strong>Home Address / GPS:</strong> {address}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Phone:</strong> {phone}</p>

    <h3>📎 Attached Documents</h3>
    <ul>
      <li>Passport: {passport.filename}</li>
      <li>Photo: {photo.filename}</li>
    </ul>
    """

    client_subject = "✅ Your VISA Application Has Been Received"
    client_body = f"""
    <p>Hi {fullName},</p>
    <p>Thank you for submitting your VISA application with 
    <strong>BentJun Travel & Tour</strong>.</p>
    <p>We’ve received your details and attached documents. 
    Our processing team will review your application and contact you soon.</p>
    <p>Best regards,<br><strong>BentJun Hub Team</strong></p>
    """

    admin_status = await send_email_async(admin_subject, admin_body, TO_EMAILS, [passport_path, photo_path])
    client_status = await send_email_async(client_subject, client_body, [email])

    if admin_status is True and client_status is True:
        return {"status": "success", "message": "✅ Application and acknowledgment emails sent successfully."}
    else:
        return {"status": "error", "message": f"Admin: {admin_status}, Client: {client_status}"}


# ==============================================================
# 🎓 Course Registration Endpoint
# ==============================================================

@app.post("/course-registration")
async def course_registration(
    studentName: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    course: str = Form(...),
    mode: str = Form(...),
    payment: str = Form(...),
    startDate: str = Form(...),
):
    """Handle online course registration form submission."""

    # Admin email
    admin_subject = f"🎓 New Course Registration from {studentName}"
    admin_body = f"""
    <h2>New Course Registration</h2>
    <p><strong>Name:</strong> {studentName}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Phone:</strong> {phone}</p>
    <p><strong>Course:</strong> {course}</p>
    <p><strong>Learning Mode:</strong> {mode}</p>
    <p><strong>Payment Plan:</strong> {payment}</p>
    <p><strong>Preferred Start Date:</strong> {startDate}</p>
    """

    # Client email
    client_subject = "✅ Course Registration Received"
    client_body = f"""
    <p>Hi {studentName},</p>
    <p>Thank you for registering for a course with <strong>BentJun Hub</strong>.</p>
    <p>We’ve received your details for the <strong>{course}</strong> program.</p>
    <p>Our training team will contact you shortly with next steps and orientation details.</p>
    <p>Best regards,<br><strong>BentJun Hub Team</strong></p>
    """

    admin_status = await send_email_async(admin_subject, admin_body, TO_EMAILS)
    client_status = await send_email_async(client_subject, client_body, [email])

    if admin_status is True and client_status is True:
        return {"status": "success", "message": "✅ Registration and confirmation emails sent successfully."}
    else:
        return {"status": "error", "message": f"Admin: {admin_status}, Client: {client_status}"}
