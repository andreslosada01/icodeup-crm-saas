from fastapi import APIRouter, Depends

from app.services.access_control import require_active_module

from . import activities, agreements, bi, channels, customers, dashboard, imports, options, payments, promises


router = APIRouter(dependencies=[Depends(require_active_module("crm"))])

for module in (options, dashboard, bi, customers, imports, activities, promises, payments, channels, agreements):
    router.include_router(module.router)
