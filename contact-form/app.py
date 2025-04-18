import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import logging

# OpenTelemetry imports
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenTelemetry setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

# FastAPI app
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

# CORS middleware for WordPress integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# POST endpoint for email submission
@app.post("/email")
async def email(request: Request):
    message_data = await request.json()
    logger.info(f"Received contact form data: {message_data}")

    with tracer.start_as_current_span("send_email") as span:
        try:
            # Add attributes for observability
            span.set_attribute("email.subject", message_data["subject"])
            span.set_attribute("email.from", message_data["email"])

            # Construct the email
            message = Mail(
                to_emails=os.environ.get("SENDGRID_TO_EMAIL"),
                from_email=os.environ.get("SENDGRID_FROM_EMAIL"),
                subject=message_data["subject"],
                html_content=f"{message_data['message']}<br />From: {message_data['name']}"
            )
            message.reply_to = message_data["email"]

            # Send using SendGrid
            sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
            response = sg.send(message)

            logger.info(f"SendGrid response: {response.status_code}")
            span.set_attribute("email.status", "success")
            span.set_status(trace.Status(trace.StatusCode.OK))

            return {"status": "success", "code": response.status_code}
        except Exception as e:
            # Handle and trace errors
            logger.error("Error sending email", exc_info=True)
            span.set_attribute("email.status", "error")
            span.set_attribute("email.error", str(e))
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            raise HTTPException(status_code=500, detail=f"SendGrid Error: {str(e)}")

# Serve static frontend (built UI)
app.mount("/", StaticFiles(directory="./dist", html=True), name="static")

# Run the app (only for direct local run)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
