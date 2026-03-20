from config import conf, settings
from fastapi_mail import MessageSchema, FastMail
from fastapi import HTTPException
import resend
resend.api_key = settings.resend_api_key

def send_email(to: str, subject: str, body: str):
    try:
        resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": subject,
        "text": body
    })
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Email failed: {str(e)}")  
async def customer_link_email(to, token):
    subject="Successful registration"
    body=f'Location: localhost:8000/customers/{token}'
    send_email(to, subject, body)

async def driver_link_email(to, token):
    subject="Successful registration"
    body=f'Location: localhost:8000/drivers/map/{token}'
    send_email(to, subject, body)

async def tenant_email(to):
    subject="Successful registration"
    body="""Hi, Your account has been created successfully. You can now log in and start managing your deliveries at onroute.onrender.com.
— OnRoute"""
    send_email(to, subject, body)