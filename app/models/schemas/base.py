from pydantic import BaseModel


class BoolResponse(BaseModel):
    ok: bool = True
