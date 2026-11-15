from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import productos_collection
from app.models.entidad_sql import ProductMaster


def reset_datos(db: Session) -> dict:
    # 1. Eliminar documentos en MongoDB (Staging)
    resultado_mongo = productos_collection.delete_many({})
    docs_eliminados = resultado_mongo.deleted_count

    # 2. Contar y truncar tabla en MySQL (Analítica)
    registros_sql = db.query(ProductMaster).count()
    db.execute(text("TRUNCATE TABLE productos_master"))
    db.commit()

    return {
        "mensaje": "Bases de datos MongoDB y MySQL reiniciadas correctamente",
        "documentos_eliminados_mongo": docs_eliminados,
        "registros_eliminados_sql": registros_sql,
    }

    import requests
from app.config import settings
from app.database import productos_collection


def extraer_datos_api(cantidad: int) -> dict:
    nuevos = 0
    ya_existentes = 0
    skip = 0
    restantes = cantidad

    while restantes > 0:
        limit = min(restantes, 100)
        response = requests.get(
            settings.API_URL,
            params={"limit": limit, "skip": skip},
            timeout=15
        )
        response.raise_for_status()
        productos = response.json().get("products", [])
        if not productos:
            break
        skip += len(productos)
        restantes -= len(productos)