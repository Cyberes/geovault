import io
import re
import zipfile

from fastkml import kml
from shapely.geometry import mapping, shape


# TODO: preserve KML object styling, such as color and opacity

def kml_to_geojson(kml_bytes):
    try:
        # Try to open as a zipfile (KMZ)
        with zipfile.ZipFile(io.BytesIO(kml_bytes), 'r') as kmz:
            # Find the first .kml file in the zipfile
            kml_file = [name for name in kmz.namelist() if name.endswith('.kml')][0]
            doc = kmz.read(kml_file).decode('utf-8')
    except zipfile.BadZipFile:
        # If not a zipfile, assume it's a KML file
        doc = kml_bytes.decode('utf-8')

    # Remove XML declaration
    doc = re.sub(r'<\?xml.*\?>', '', doc)

    k = kml.KML()
    k.from_string(doc)

    features = []
    process_feature(features, k)

    return {
        'type': 'FeatureCollection',
        'features': features
    }


def process_feature(features, feature):
    # Recursive function to handle folders within folders
    if isinstance(feature, (kml.Document, kml.Folder, kml.KML)):
        for child in feature.features():
            process_feature(features, child)
    elif isinstance(feature, kml.Placemark):
        geom = shape(feature.geometry)
        # Only keep points, lines and polygons
        if geom.geom_type in ['Point', 'LineString', 'Polygon']:
            features.append({
                'type': 'Feature',
                'properties': {
                    'name': feature.name,
                    'description': feature.description,
                },
                'geometry': mapping(geom),
            })
            if feature.extended_data is not None:
                features['properties'].update(feature.extended_data)
    else:
        # raise ValueError(f'Unknown feature: {type(feature)}')
        pass
