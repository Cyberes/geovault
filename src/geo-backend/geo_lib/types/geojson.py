from typing import Optional, List

from pydantic import BaseModel, Field


class GeojsonRawProperty(BaseModel):
    # A class to whitelist these properties.
    name: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list, alias='feature_tags')  # kml2geojson calls this field `feature_tags`
