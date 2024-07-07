from datetime import datetime
from typing import List

from geo_lib.types.item import GeoFeature


def generate_auto_tags(feature: GeoFeature) -> List[str]:
    tags = []
    tags.append(f'type:{feature.geometry.type.value}')
    now = datetime.now()
    tags.append(f'year:{now.year}')
    tags.append(f'month:{now.strftime("%B")}')
    return [str(x) for x in tags]
