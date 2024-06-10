from typing import Optional

from pydantic import BaseModel


class GeojsonRawProperty(BaseModel):
    # Whitelist these properties.
    name: str
    description: Optional[str] = None
