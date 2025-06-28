from typing import Dict, Optional, Any

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]


class TokenPayload(BaseModel):
    sub: Optional[str] = None 