import json
import base64
import os
from datetime import datetime
import pytz
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

private_key_path = os.getenv('PRIVATE_KEY_PATH')

with open(private_key_path, 'rb') as file:
    private_key = serialization.load_pem_private_key(file.read(), password=None)


def sign_session(national_code: str, birthdate: str):
    # Define the GMT time zone
    gmt_tz = pytz.timezone('GMT')

    # Convert the birthdate from string (format: YYYY-MM-DD) to a naive datetime object
    birthdate_datetime = datetime.strptime(birthdate, "%Y-%m-%d")

    # Set the time to 08:30 AM
    birthdate_with_time = birthdate_datetime.replace(hour=8, minute=30)

    # Localize the datetime object to GMT
    birthdate_gmt = gmt_tz.localize(birthdate_with_time)

    payload = {
        "national_code": str(national_code),
        "birthdate": int(birthdate_gmt.timestamp()),
        "timestamp": int(datetime.now().timestamp())
    }

    payload_json = json.dumps(payload).encode()

    # Sign the payload
    signature = private_key.sign(
        data=payload_json,
        padding=padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        algorithm=hashes.SHA256()
    )

    # Encode the payload and signature
    signature_base64 = base64.urlsafe_b64encode(signature).decode()
    payload_base64 = base64.urlsafe_b64encode(payload_json).decode()

    # Return the final payload
    return f"{payload_base64}.{signature_base64}"


def sign_verification(token: str):
    payload = {
        "validation_token": str(token),
    }

    payload_json = json.dumps(payload).encode()

    # Sign the payload
    signature = private_key.sign(
        data=payload_json,
        padding=padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        algorithm=hashes.SHA256()
    )

    # Encode the payload and signature
    signature_base64 = base64.urlsafe_b64encode(signature).decode()
    payload_base64 = base64.urlsafe_b64encode(payload_json).decode()

    # Return the final payload
    return f"{payload_base64}.{signature_base64}"
