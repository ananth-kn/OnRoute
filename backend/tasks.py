from celery import Celery
from config import conf
import asyncio
from fastapi_mail import MessageSchema, FastMail

app = Celery('tasks', broker='redis://localhost')

@app.task
def customer_link_email(to, token):
    try:
        message = MessageSchema(subject="Successful registration",recipients=[to],
        body=f'Location: localhost:8000/customers/{token}',subtype="plain")
        fm = FastMail(conf)
        fm.send_message(message)
    except Exception as e:
        print(f"Email failed for {to}: {str(e)}")
        raise

@app.task
def driver_link_email(to, token):
    try:
        print("sending email")
        message = MessageSchema(subject="Successful registration",recipients=[to],
        body=f'Location: localhost:8000/drivers/map/{token}',subtype="plain")
        fm = FastMail(conf)
        asyncio.run(fm.send_message(message))
    except Exception as e:
        print(f"Email failed for {to}: {str(e)}")
        raise

@app.task
def tenant_email(to):
    try:
        message = MessageSchema(subject="Successful registration",recipients=[to],
        body=f"Success",subtype="plain")
        fm = FastMail(conf)
        asyncio.run(fm.send_message(message))
    except Exception as e:
        print(f"Email failed for {to}: {str(e)}")
        raise