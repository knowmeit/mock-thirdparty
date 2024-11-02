import logging
import os

import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from app.schemas import TakeResultResponse, SessionRequest

from utils import sign_session

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the FastAPI app
app = FastAPI(debug=True)

# Validate environment variables at startup
allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(",")
face_server = os.getenv('FACE_SERVER_URL', 'https://api.know-me.ir')
if not face_server:
    logger.error("FACE_SERVER_URL environment variable is missing.")
    raise ValueError("FACE_SERVER_URL environment variable is required.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = [
        f"Field {'.'.join(str(loc) for loc in error['loc'][1:])}: {error['msg']}"
        for error in errors
    ]
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "errors": error_messages
        }
    )

@app.post("/create_session")
async def create_session(request: SessionRequest, http_request: Request):
    logger.info("Received create session request")
    try:
        # Check for SERVICE-ID header
        service_id = http_request.headers.get("SERVICE-ID")
        if not service_id:
            logger.warning("SERVICE-ID header is missing")
            raise HTTPException(status_code=400, detail="SERVICE-ID header is missing.")

        # Prepare and sign payload
        signed_payload = sign_session(request.national_code, request.birthdate)
        logger.debug(f"Signed payload: {signed_payload}")

        # Define request data and headers
        post_data = {"payload": signed_payload}
        headers = {"SERVICE-ID": service_id, "Content-Type": "application/json"}

        # Make API request with a timeout
        try:
            response = requests.post(
                f"{face_server}/v2/sessions/",
                headers=headers,
                json=post_data,
                timeout=5
            )
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx status codes

            response_json = response.json()
            token = response_json.get('data', {}).get('token', '')

            if not token:
                logger.warning("Token not found in response")
                raise HTTPException(status_code=502, detail="Token missing in response.")

            return {"token": token}

        except Timeout:
            logger.error("Request to face server timed out")
            raise HTTPException(status_code=504, detail="Request to face server timed out.")
        except RequestException as e:
            logger.error(f"Request failed: {e}")
            raise HTTPException(status_code=502, detail="Error communicating with face server.")

    except Exception as e:
        logger.exception(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/take_result")
async def take_result(data: TakeResultResponse):
    # if data and data.similarity is not None:
    #     if not (0 <= data.attributes.similarity <= 1):
    #         raise HTTPException(status_code=400, detail="Similarity must be between 0 and 1")

    print(f"Received data from callback: {data.model_dump()}")

    return {"message": "Data received successfully", "data": data.model_dump(exclude_unset=True)}
