from config import conf
from fastapi_mail import MessageSchema, FastMail


async def customer_link_email(to, token):
    try:
        message = MessageSchema(subject="Successful registration",recipients=[to],
        body=f'Location: localhost:8000/customers/{token}',subtype="plain")
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"Email failed for {to}: {str(e)}")
        raise

async def driver_link_email(to, token):
    try:
        print("sending email")
        message = MessageSchema(subject="Successful registration",recipients=[to],
        body=f'Location: localhost:8000/drivers/map/{token}',subtype="plain")
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"Email failed for {to}: {str(e)}")
        raise

async def tenant_email(to):
    try:
        message = MessageSchema(subject="Successful registration",recipients=[to],
        body=f"Success",subtype="plain")
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"Email failed for {to}: {str(e)}")
        raise