from fastapi import APIRouter

from . import activities, agreements, bi, channels, customers, dashboard, imports, options, payments, promises


router = APIRouter()

for module in (options, dashboard, bi, customers, imports, activities, promises, payments, channels, agreements):
    router.include_router(module.router)
