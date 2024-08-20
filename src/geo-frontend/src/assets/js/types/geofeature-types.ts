enum GeoFeatureType {
    POINT = 'Point',
    LINESTRING = 'LineString',
    POLYGON = 'Polygon'
}

interface GeoFeatureProps {
    name: string;
    id: number;
    type: GeoFeatureType;
    description?: string;
    tags?: string[];
    geometry: any[];
}

class GeoFeature {
    name: string;
    id: number;
    type: GeoFeatureType;
    description?: string;
    tags: string[] = [];
    geometry: any[];

    constructor(props: GeoFeatureProps) {
        this.name = props.name;
        this.id = props.id;
        this.type = props.type;
        this.description = props.description;
        this.tags = props.tags || [];
        this.geometry = props.geometry || [];
    }
}

export class GeoPoint extends GeoFeature {
    type: GeoFeatureType = GeoFeatureType.POINT;
    geometry: number[];

    constructor(props: GeoFeatureProps) {
        super({...props, type: GeoFeatureType.POINT});
    }
}

export class GeoLineString extends GeoFeature {
    type: GeoFeatureType = GeoFeatureType.LINESTRING;
    geometry: number[][];

    constructor(props: GeoFeatureProps) {
        super({...props, type: GeoFeatureType.LINESTRING});
    }
}

export class GeoPolygon extends GeoFeature {
    type: GeoFeatureType = GeoFeatureType.POLYGON;
    geometry: number[][][];

    constructor(props: GeoFeatureProps) {
        super({...props, type: GeoFeatureType.POLYGON});
    }
}
