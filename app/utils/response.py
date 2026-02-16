from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None

def create_response(data: Any, message: str = "Success") -> APIResponse:
    return APIResponse(data=data, message=message)
