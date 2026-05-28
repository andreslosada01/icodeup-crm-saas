from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import administration, auth, crm, documents, health, legal, sales, subscriptions, tenants, typifications
from app.core.config import settings
from app.db.session import SessionLocal, init_database
from app.services.bootstrap_service import bootstrap_platform


app = FastAPI(title=settings.app_name)

frontend_dir = Path(settings.frontend_dir)
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"), name="assets")

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(administration.router, prefix="/api/admin", tags=["administration"])
app.include_router(crm.router, prefix="/api/crm", tags=["crm"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(legal.router, prefix="/api/legal", tags=["legal"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])
app.include_router(typifications.router, prefix="/api/typifications", tags=["typifications"])


@app.on_event("startup")
def startup() -> None:
    result = init_database()
    if result["ok"] and SessionLocal is not None:
        with SessionLocal() as db:
            bootstrap_platform(db)


@app.get("/", response_model=None)
def frontend():
    index = frontend_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"app": settings.app_name, "detail": "Frontend no construido."}
