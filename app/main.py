from fastapi import FastAPI
from app.controllers import etl_controller
from app.database import Base, engine
from app.models import entidad_sql  # noqa: F401

app = FastAPI(
    title="Laboratorio ETL - Pipeline Híbrido (MongoDB + MySQL)",
    description="API REST bajo arquitectura MVC para extracción, transformación, carga y analítica de datos.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[Advertencia Startup MySQL] No se pudo conectar aún a MySQL: {e}")


app.include_router(etl_controller.router)


@app.get("/", tags=["Healthcheck"])
def healthcheck():
    return {
        "estado": "activo",
        "mensaje": "API ETL Hybrid Pipeline funcionando correctamente",
        "documentacion": "/docs",
    }