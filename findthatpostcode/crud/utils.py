from typing import Type, overload

from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Document
from fastapi import HTTPException

from findthatpostcode.schema.db import Area as AreaDocument
from findthatpostcode.schema.db import Place as PlaceDocument
from findthatpostcode.schema.db import Postcode as PostcodeDocument


@overload
def get_or_404(
    document: Type[AreaDocument], es: Elasticsearch, id: str, **kwargs
) -> AreaDocument: ...
@overload
def get_or_404(
    document: Type[PostcodeDocument], es: Elasticsearch, id: str, **kwargs
) -> PostcodeDocument: ...
@overload
def get_or_404(
    document: Type[PlaceDocument], es: Elasticsearch, id: str, **kwargs
) -> PlaceDocument: ...
def get_or_404(
    document: Type[Document], es: Elasticsearch, id: str, **kwargs
) -> Document:
    try:
        result = document.get(id, using=es, **kwargs)
        if result:
            return result
    except NotFoundError:
        raise HTTPException(
            status_code=404, detail=f"{document.__name__} {id} not found"
        )
    raise HTTPException(status_code=404, detail=f"{document.__name__} {id} not found")
