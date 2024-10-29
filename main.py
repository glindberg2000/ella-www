import logging
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/home/plato/dev/ella_www/.env')

# Minimal logging setup - console only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ella_app")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        logger.error("SendGrid API key not found in environment variables")
        return JSONResponse(
            status_code=500,
            content={"detail": "Email service not configured"}
        )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
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
        response = sg.send(mail)
        return JSONResponse(
            status_code=200,
            content={"message": "Message sent successfully! We'll get back to you soon."}
        )
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to send message. Please try again."}
        )

# Serve static files from the 'ella_www' directory after defining API routes
app.mount("/", StaticFiles(directory="/home/plato/dev/ella_www", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)