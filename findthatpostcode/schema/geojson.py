import enum
from typing import Any, Literal

from pydantic import BaseModel


class GeometryType(enum.StrEnum):
    POINT = "Point"
    MULTI_POINT = "MultiPoint"
    LINE_STRING = "LineString"
    MULTI_LINE_STRING = "MultiLineString"
    POLYGON = "Polygon"
    MULTI_POLYGON = "MultiPolygon"


GEOMETRY_COLLECTION = "GeometryCollection"


class GeoJSONType(enum.StrEnum):
    POINT = GeometryType.POINT
    MULTI_POINT = GeometryType.MULTI_POINT
    LINE_STRING = GeometryType.LINE_STRING
    MULTI_LINE_STRING = GeometryType.MULTI_LINE_STRING
    POLYGON = GeometryType.POLYGON
    MULTI_POLYGON = GeometryType.MULTI_POLYGON
    GEOMETRY_COLLECTION = GEOMETRY_COLLECTION
    FEATURE = "Feature"
    FEATURE_COLLECTION = "FeatureCollection"


Position = list[float]  # [lon, lat]
MultiPoint = list[Position]
LineString = list[Position]
MultiLineString = list[LineString]
LinearRing = LineString
Polygon = list[LinearRing]


class GeometryPoint(BaseModel):
    type: Literal[GeometryType.POINT] = GeometryType.POINT
    coordinates: Position = []  # [lon, lat]
    bbox: list[float] | None = None


class GeometryMultiPoint(BaseModel):
    type: Literal[GeometryType.MULTI_POINT] = GeometryType.MULTI_POINT
    coordinates: MultiPoint = []  # [[lon, lat]]
    bbox: list[float] | None = None


class GeometryLineString(BaseModel):
    type: Literal[GeometryType.LINE_STRING] = GeometryType.LINE_STRING
    coordinates: LineString = []  # [[lon, lat]]
    bbox: list[float] | None = None


class GeometryMultiLineString(BaseModel):
    type: Literal[GeometryType.MULTI_LINE_STRING] = GeometryType.MULTI_LINE_STRING
    coordinates: MultiLineString = []  # [[lon, lat]]
    bbox: list[float] | None = None


class GeometryPolygon(BaseModel):
    type: Literal[GeometryType.POLYGON] = GeometryType.POLYGON
    coordinates: Polygon = []  # [[lon, lat]]
    bbox: list[float] | None = None


class GeometryMultiPolygon(BaseModel):
    type: Literal[GeometryType.MULTI_POLYGON] = GeometryType.MULTI_POLYGON
    coordinates: list[Polygon] = []  # [[[lon, lat]]]
    bbox: list[float] | None = None


Geometry = (
    GeometryPoint
    | GeometryMultiPoint
    | GeometryLineString
    | GeometryMultiLineString
    | GeometryPolygon
    | GeometryMultiPolygon
)


class GeometryCollection(BaseModel):
    type: Literal["GeometryCollection"] = GEOMETRY_COLLECTION
    geometries: list[Geometry] = []
    bbox: list[float] | None = None


class Feature(BaseModel):
    type: Literal[GeoJSONType.FEATURE] = GeoJSONType.FEATURE
    geometry: Geometry | GeometryCollection | None = None
    properties: dict[str, Any] | None = None
    id: str | None = None
    bbox: list[float] | None = None


class FeatureCollection(BaseModel):
    type: Literal[GeoJSONType.FEATURE_COLLECTION] = GeoJSONType.FEATURE_COLLECTION
    features: list[Feature] = []
    bbox: list[float] | None = None


def geometry_from_dict(data: dict[str, Any]) -> Geometry | GeometryCollection | None:
    geom_type = data.get("type")
    if geom_type == GeometryType.POINT:
        return GeometryPoint(**data)
    elif geom_type == GeometryType.MULTI_POINT:
        return GeometryMultiPoint(**data)
    elif geom_type == GeometryType.LINE_STRING:
        return GeometryLineString(**data)
    elif geom_type == GeometryType.MULTI_LINE_STRING:
        return GeometryMultiLineString(**data)
    elif geom_type == GeometryType.POLYGON:
        return GeometryPolygon(**data)
    elif geom_type == GeometryType.MULTI_POLYGON:
        return GeometryMultiPolygon(**data)
    elif geom_type == GEOMETRY_COLLECTION:
        return GeometryCollection(**data)
    return None
