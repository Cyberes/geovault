from enum import Enum
from typing import Tuple, Optional, List

from pydantic import Field, BaseModel


class GeoFeatureType(Enum):
    POINT = 'Point'
    LINESTRING = 'LineString'
    POLYGON = 'Polygon'


class GeoFeatureGeomoetry(BaseModel):
    type: GeoFeatureType
    coordinates: List[float] | List[List[float]] | List[List[List[float]]]


class GeoFeature(BaseModel):
    """
    A thing that's shown on the map.
    Can be a point, linestring, or polygon.
    """
    name: str
    id: int  # From the database
    type: GeoFeatureType
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    geometry: GeoFeatureGeomoetry


def geojson_to_geofeature(geojson: dict) -> List[GeoFeature]:
    result = []
    for item in geojson['features']:
        result.append(
            GeoFeature(
                name=item['properties']['title'],
                id=-1,  # This will be updated after it's added to the main data store.
                type=GeoFeatureType(item['geometry']['type']),
                description=item['properties']['description'],
                tags=item['properties']['feature_tags'],
                geometry=GeoFeatureGeomoetry(**item['geometry'])
            )
        )
    return result
