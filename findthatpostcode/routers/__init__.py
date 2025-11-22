from fastapi import APIRouter, Depends

from findthatpostcode.routers.areas import router as areas_router
from findthatpostcode.routers.areatype import router as areatype_router
from findthatpostcode.routers.place import router as place_router
from findthatpostcode.routers.postcodes import router as postcodes_router
from findthatpostcode.security import api_key_scheme

router = APIRouter(dependencies=[Depends(api_key_scheme)])

router.include_router(postcodes_router, prefix="/postcodes")
router.include_router(areas_router, prefix="/areas")
router.include_router(areatype_router, prefix="/areatypes")
router.include_router(place_router, prefix="/places")
