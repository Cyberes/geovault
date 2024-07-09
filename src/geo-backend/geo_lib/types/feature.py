from enum import Enum
from typing import Optional, List, Union, Tuple

from pydantic import Field, BaseModel

from geo_lib.daemon.workers.workers_lib.importer.logging import create_import_log_msg


class GeoFeatureType(str, Enum):
    POINT = 'Point'
    LINESTRING = 'LineString'
    POLYGON = 'Polygon'


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
    geometry: List


class GeoPoint(GeoFeature):
    type: GeoFeatureType = GeoFeatureType.POINT
    geometry: List[float]


class GeoLineString(GeoFeature):
    type: GeoFeatureType = GeoFeatureType.LINESTRING
    geometry: List[List[float]]


class GeoPolygon(GeoFeature):
    type: GeoFeatureType = GeoFeatureType.POLYGON
    geometry: List[List[List[float]]]


GeoFeatureSupported = Union[GeoPoint, GeoLineString, GeoPolygon]


def geojson_to_geofeature(geojson: dict) -> Tuple[List[GeoFeatureSupported], List[str]]:
    result = []
    log = []
    for item in geojson['features']:
        match item['geometry']['type'].lower():
            case 'point':
                c = GeoPoint
            case 'linestring':
                c = GeoLineString
            case 'polygon':
                c = GeoPolygon
            case _:
                log.append(create_import_log_msg(f'Feature named "{item["properties"]["title"]}" had unsupported type "{item["geometry"]["type"]}".'))
                continue
        result.append(c(
            name=item['properties']['title'],
            id=-1,  # This will be updated after it's added to the main data store.
            description=item['properties']['description'],
            tags=item['properties']['feature_tags'],
            geometry=item['geometry']['coordinates']
        ))

    return result, log
