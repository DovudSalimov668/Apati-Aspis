from pydantic import BaseModel, Field
from typing import List

class PasswordCheckRequest(BaseModel):
    password: str = Field(..., description="Plaintext password to check locally via K-Anonymity SHA-1 prefix")

class PasswordCheckResponse(BaseModel):
    is_pwned: bool
    breach_count: int
    sha1_prefix: str
    message: str
    disclaimer: str
    recommendations: List[str]
