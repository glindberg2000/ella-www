import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ella_app")

# Add file handler
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

app = FastAPI()

# Health check endpoint
@app.get("/api/health")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

# Dummy post endpoint
@app.post("/dummy-post")
async def dummy_post(name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    logging.info(f"Received dummy post: name={name}, email={email}, message={message}")
    return JSONResponse({"name": name, "email": email, "message": message})

# Send email endpoint
@app.post("/send-email")
async def send_email(name: str = Form(...), email: EmailStr = Form(...), message: str = Form(...)):
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    if not SENDGRID_API_KEY:
        return JSONResponse({"message": "SendGrid API key not found"}, status_code=500)
    
    mail = Mail(
        from_email='info@ella-ai-care.com',
        to_emails='realcryptoplato@gmail.com',
        subject='New Contact Form Submission',
        html_content=f"""
        <strong>New contact form submission</strong><br>
        <strong>Name:</strong> {name}<br>
        <strong>Email:</strong> {email}<br>
        <strong>Message:</strong> {message}
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)
    except Exception as e:
        return JSONResponse({"message": "Failed to send email"}, status_code=500)
    
    return JSONResponse({"message": "Email sent successfully"})

# Import and include the ChatGPT router
from robloxgpt import router as chatgpt_router
app.include_router(chatgpt_router)

# Serve static files from the 'ella_www' directory after defining API routes
app.mount("/", StaticFiles(directory="/home/plato/dev/ella_www", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)