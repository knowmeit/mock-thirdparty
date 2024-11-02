from typing import Optional

from pydantic import BaseModel, Field


class TakeResultResponse(BaseModel):
    national_code: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate: Optional[str] = None
    father_name: Optional[str] = None
    expire_date: Optional[str] = None
    similarity: Optional[float] = None
    verification_flag: Optional[bool] = Field(None, alias="verification-flag")
    liveness_flag: Optional[bool] = Field(None, alias="liveness-flag")