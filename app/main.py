import logging
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from app.schemas import TakeResultResponse

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the FastAPI app
app = FastAPI(debug=True)

# Validate environment variables at startup
allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(",")

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

@app.post("/take_result")
async def take_result(data: TakeResultResponse):
    # if data and data.similarity is not None:
    #     if not (0 <= data.attributes.similarity <= 1):
    #         raise HTTPException(status_code=400, detail="Similarity must be between 0 and 1")

    print(f"Received data from callback: {data.model_dump()}")

    return {"message": "Data received successfully", "data": data.model_dump(exclude_unset=True)}
