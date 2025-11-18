from fastapi import APIRouter

from findthatpostcode.routers.postcodes import router as postcodes_router

router = APIRouter()

router.include_router(postcodes_router, prefix="/postcodes")
