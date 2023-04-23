from typing import Dict, Any

from pydantic import BaseModel


class BoolResponse(BaseModel):
    ok: bool = True
    additional_info: Dict[Any, Any] = {}
