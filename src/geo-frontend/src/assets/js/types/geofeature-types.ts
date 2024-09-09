enum GeoFeatureType {
    POINT = 'Point',
    LINESTRING = 'LineString',
    POLYGON = 'Polygon'
}

interface GeoFeatureProperties {
    created: Date;
    software: string;
    software_version: string;
    tags: string[];
}

interface GeoFeatureProps {
    name: string;
    id: number;
    type: GeoFeatureType;
    description?: string;
    geometry: any[];
    properties: GeoFeatureProperties;
}

class GeoFeature {
    name: string;
    id: number;
    type: GeoFeatureType;
    description?: string;
    tags: string[] = [];
    geometry: any[];
    properties: GeoFeatureProperties;

    constructor(props: GeoFeatureProps) {
        this.name = props.name;
        this.id = props.id;
        this.type = props.type;
        this.description = props.description;
        this.geometry = props.geometry || [];
        this.properties = props.properties;
    }
}

export class GeoPoint extends GeoFeature {
    type: GeoFeatureType = GeoFeatureType.POINT;
    geometry: number[];
}

export class GeoLineString extends GeoFeature {
    type: GeoFeatureType = GeoFeatureType.LINESTRING;
    geometry: number[][];
}

export class GeoPolygon extends GeoFeature {
    type: GeoFeatureType = GeoFeatureType.POLYGON;
    geometry: number[][][];
}
