from typing import Optional, List

from pydantic import BaseModel, Field


class GeojsonRawProperty(BaseModel):
    # A class to whitelist these properties.
    name: str
    description: Optional[str] = None
    feature_tags: List[str] = Field(default_factory=list)
