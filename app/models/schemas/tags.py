from typing import Optional

from pydantic import BaseModel, Field


class TagsInCreate(BaseModel):
    name: str = Field(max_length=72)
    short_description: str = Field(max_length=100)
    # parent_tag_id: Optional[int]
