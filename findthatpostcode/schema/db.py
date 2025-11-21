from datetime import datetime
from typing import Optional

from elasticsearch import Elasticsearch
from elasticsearch_dsl import (
    Boolean,
    Date,
    Document,
    Float,
    GeoPoint,
    InnerDoc,
    Keyword,
    Long,
    Nested,
    Text,
)

from findthatpostcode.schema import Area as AreaSchema
from findthatpostcode.schema import (
    AreaBase,
    AreaEquivalents,
    Location,
    PostcodeAreas,
    StatutoryInstrument,
)
from findthatpostcode.schema import Place as PlaceSchema
from findthatpostcode.schema import Postcode as PostcodeSchema
from findthatpostcode.settings import AREA_INDEX, PLACENAME_INDEX, POSTCODE_INDEX


class Postcode(Document):
    pcd: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    pcd2: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    pcds: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    dointr: Optional[datetime] = Date()  # pyright: ignore[reportAssignmentType]
    doterm: Optional[datetime] = Date()  # pyright: ignore[reportAssignmentType]
    usertype: Optional[int] = Long()  # pyright: ignore[reportAssignmentType]
    oseast1m: Optional[int] = Long()  # pyright: ignore[reportAssignmentType]
    osnrth1m: Optional[int] = Long()  # pyright: ignore[reportAssignmentType]
    osgrdind: Optional[int] = Long()  # pyright: ignore[reportAssignmentType]
    oa21: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    cty: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ced: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    laua: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ward: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    nhser: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ctry: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    rgn: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    pcon: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ttwa: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    itl: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    park: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lsoa21: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    msoa21: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    wz11: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    sicbl: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    bua24: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ruc21: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    oac11: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lat: Optional[str] = Float()  # pyright: ignore[reportAssignmentType]
    long: Optional[str] = Float()  # pyright: ignore[reportAssignmentType]
    lep1: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lep2: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    pfa: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    imd: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    icb: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    location: Optional[dict[str, float]] = GeoPoint()  # pyright: ignore[reportAssignmentType]
    hash: Optional[str] = Text(index_prefixes={"min_chars": 2, "max_chars": 5})  # pyright: ignore[reportAssignmentType]
    wd: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lad: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    pcd7: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    pcd8: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    msoa11: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    oa11: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lsoa11: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]

    class Index:
        name = POSTCODE_INDEX

    def to_schema(self, es: Elasticsearch | None = None) -> PostcodeSchema:
        areas = PostcodeAreas(
            bua24=get_area_base(self.bua24, es),
            ced=get_area_base(self.ced, es),
            ctry=get_area_base(self.ctry, es),
            cty=get_area_base(self.cty, es),
            icb=get_area_base(self.icb, es),
            itl=get_area_base(self.itl, es),
            lad=get_area_base(self.lad, es),
            laua=get_area_base(self.laua, es),
            lep1=get_area_base(self.lep1, es),
            lep2=get_area_base(self.lep2, es),
            lsoa11=get_area_base(self.lsoa11, es),
            lsoa21=get_area_base(self.lsoa21, es),
            msoa11=get_area_base(self.msoa11, es),
            msoa21=get_area_base(self.msoa21, es),
            nhser=get_area_base(self.nhser, es),
            oa11=get_area_base(self.oa11, es),
            oa21=get_area_base(self.oa21, es),
            park=get_area_base(self.park, es),
            pcon=get_area_base(self.pcon, es),
            pfa=get_area_base(self.pfa, es),
            rgn=get_area_base(self.rgn, es),
            sicbl=get_area_base(self.sicbl, es),
            ttwa=get_area_base(self.ttwa, es),
            ward=get_area_base(self.ward, es),
            wd=get_area_base(self.wd, es),
            wz11=get_area_base(self.wz11, es),
        )
        return PostcodeSchema(
            dointr=self.dointr,
            doterm=self.doterm,
            location=Location(
                lat=self.location["lat"] if self.location else None,
                lon=self.location["lon"] if self.location else None,
                oseast1m=self.oseast1m,
                osgrdind=self.osgrdind,
                osnrth1m=self.osnrth1m,
            ),
            pcd=self.pcd,
            pcd2=self.pcd2,
            pcd7=self.pcd7,
            pcd8=self.pcd8,
            pcds=self.pcds,
            usertype=self.usertype,
            areas=areas,
            # stats=self.stats,  # @todo Implement stats mapping
        )


class Equivalents(InnerDoc):
    mhclg: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    nhs: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ons: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    scottish_government: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    welsh_government: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]

    def to_schema(self, es: Elasticsearch | None = None) -> AreaEquivalents:
        return AreaEquivalents(
            mhclg=self.mhclg,
            nhs=self.nhs,
            ons=self.ons,
            scottish_government=self.scottish_government,
            welsh_government=self.welsh_government,
        )


class Area(Document):
    code: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    name: Optional[str] = Text()  # pyright: ignore[reportAssignmentType]
    name_welsh: Optional[str] = Text()  # pyright: ignore[reportAssignmentType]
    statutory_instrument_id: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    statutory_instrument_title: Optional[str] = Text()  # pyright: ignore[reportAssignmentType]
    date_start: Optional[datetime] = Date()  # pyright: ignore[reportAssignmentType]
    date_end: Optional[datetime] = Date()  # pyright: ignore[reportAssignmentType]
    parent: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    entity: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    owner: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    active: Optional[bool] = Boolean()  # pyright: ignore[reportAssignmentType]
    areaehect: Optional[float] = Float()  # pyright: ignore[reportAssignmentType]
    areachect: Optional[float] = Float()  # pyright: ignore[reportAssignmentType]
    areaihect: Optional[float] = Float()  # pyright: ignore[reportAssignmentType]
    arealhect: Optional[float] = Float()  # pyright: ignore[reportAssignmentType]
    sort_order: Optional[int] = Keyword()  # pyright: ignore[reportAssignmentType]
    predecessor: Optional[list[str]] = Keyword()  # pyright: ignore[reportAssignmentType]
    successor: Optional[list[str]] = Keyword()  # pyright: ignore[reportAssignmentType]
    equivalents: Optional[Equivalents] = Nested(Equivalents)  # pyright: ignore[reportAssignmentType]
    type: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    alternative_names: Optional[list[str]] = Text()  # pyright: ignore[reportAssignmentType]

    class Index:
        name = AREA_INDEX

    @classmethod
    def get_name(cls, id, using=None, index=None, **kwargs) -> str | None:
        result = super().get(
            id, using=using, index=index, _source_includes=["name"], **kwargs
        )
        if result:
            return result.name
        return None

    def to_base_schema(self) -> AreaBase:
        return AreaBase(code=self.code, name=self.name)

    def to_schema(self, es: Elasticsearch | None = None) -> AreaSchema:
        return AreaSchema(
            code=self.code,
            name=self.name,
            active=self.active if self.active is not None else True,
            alternative_names=self.alternative_names if self.alternative_names else [],
            areachect=self.areachect,
            areaehect=self.areaehect,
            areaihect=self.areaihect,
            arealhect=self.arealhect,
            date_end=self.date_end,
            date_start=self.date_start,
            entity=self.entity,
            equivalents=self.equivalents.to_schema(es) if self.equivalents else None,
            name_welsh=self.name_welsh,
            owner=self.owner,
            statutory_instrument=StatutoryInstrument(
                id=self.statutory_instrument_id,
                title=self.statutory_instrument_title,
            ),
        )


def get_area_base(
    areacode: str | None, es: Elasticsearch | None = None
) -> AreaBase | None:
    if not areacode or not es:
        return AreaBase(code=areacode) if areacode else None
    doc = Area.get_name(areacode, using=es)
    if doc:
        return AreaBase(code=areacode, name=doc)
    return None


class PlaceAreas(InnerDoc):
    bua22: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    cty: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    laua: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ward: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    parish: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    hlth: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    rgd: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    rgn: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    park: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    pcon: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    eer: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    pfa: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]


class Place(Document):
    tempcode: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    placeid: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    place23cd: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    placesort: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    splitind: Optional[bool] = Boolean()  # pyright: ignore[reportAssignmentType]
    descnm: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ctyhistnm: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    cty61nm: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    cty91nm: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ctyltnm: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ctry23nm: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lad61nm: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lad61desc: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lad91nm: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lad91desc: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lad23desc: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    ced23cd: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    gridgb1m: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    gridgb1e: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    gridgb1n: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    grid1km: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    lat: Optional[float] = Float()  # pyright: ignore[reportAssignmentType]
    long: Optional[float] = Float()  # pyright: ignore[reportAssignmentType]
    name: Optional[str] = Text()  # pyright: ignore[reportAssignmentType]
    location: Optional[dict[str, float]] = GeoPoint()  # pyright: ignore[reportAssignmentType]
    areas: Optional[PlaceAreas] = Nested(PlaceAreas)  # pyright: ignore[reportAssignmentType]
    type: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]
    country: Optional[str] = Keyword()  # pyright: ignore[reportAssignmentType]

    class Index:
        name = PLACENAME_INDEX

    def to_schema(self, es: Elasticsearch | None = None) -> PlaceSchema:
        return PlaceSchema(
            code=self.place23cd,
            name=self.name,
            location=Location(
                lat=self.location["lat"] if self.location else None,
                lon=self.location["lon"] if self.location else None,
            ),
            type=self.type,
            country=self.country,
            areas=PostcodeAreas(
                bua22=get_area_base(self.areas.bua22 if self.areas else None, es),
                cty=get_area_base(self.areas.cty if self.areas else None, es),
                laua=get_area_base(self.areas.laua if self.areas else None, es),
                ward=get_area_base(self.areas.ward if self.areas else None, es),
                parish=get_area_base(self.areas.parish if self.areas else None, es),
                hlth=get_area_base(self.areas.hlth if self.areas else None, es),
                rgd=get_area_base(self.areas.rgd if self.areas else None, es),
                rgn=get_area_base(self.areas.rgn if self.areas else None, es),
                park=get_area_base(self.areas.park if self.areas else None, es),
                pcon=get_area_base(self.areas.pcon if self.areas else None, es),
                eer=get_area_base(self.areas.eer if self.areas else None, es),
                pfa=get_area_base(self.areas.pfa if self.areas else None, es),
            ),
        )
