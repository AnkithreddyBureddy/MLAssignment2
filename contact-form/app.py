import uvicorn
from fastapi import FastAPI, Request
from fastapi import HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/email")
async def email(request: Request):
    messageContents = await request.json()
    message = Mail(
        to_emails=os.environ.get('SENDGRID_TO_EMAIL'),
        from_email=os.environ.get('SENDGRID_FROM_EMAIL'),
        subject=messageContents["subject"],
        html_content= f"{messageContents["message"]}<br />{messageContents["name"]}")
    message.reply_to = messageContents["email"]

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response
    except Exception as e:
        return e
    

app.mount('/', StaticFiles(directory="./dist", html=True), name="src")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)