from config import conf, settings
from fastapi_mail import MessageSchema, FastMail
from fastapi import HTTPException
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def send_email(to: str, subject: str, body: str):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.brevo_api_key
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to}],
        sender={"email": "newkairos.now@gmail.com", "name": "OnRoute"},
        subject=subject,
        text_content=body
    )
    
    # try:
    api_instance.send_transac_email(send_smtp_email)
    # except ApiException as e:
    #     raise HTTPException(status_code=503, detail=f"Email failed: {str(e)}")
     
async def customer_link_email(to, token):
    subject="Successful registration"
    body=f'Location: https://onroute.onrender.com/customers/{token}'
    send_email(to, subject, body)

async def driver_link_email(to, token):
    subject="Successful registration"
    body=f'Location: https://onroute.onrender.com/drivers/map/{token}'
    send_email(to, subject, body)

async def tenant_email(to):
    subject="Successful registration"
    body="""Hi, Your account has been created successfully. You can now log in and start managing your deliveries at onroute.onrender.com.
— OnRoute"""
    send_email(to, subject, body)