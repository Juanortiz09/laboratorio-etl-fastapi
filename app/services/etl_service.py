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
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")

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

        for prod in productos:
            prod_id = prod["id"]
            documento = dict(prod)
            documento["_id"] = prod_id

            resultado = productos_collection.update_one(
                {"_id": prod_id},
                {"$setOnInsert": documento},
                upsert=True
            )
            if resultado.upserted_id is not None:
                nuevos += 1
            else:
                ya_existentes += 1

        skip += len(productos)
        restantes -= len(productos)

    return {
        "mensaje": "Datos extraídos exitosamente desde DummyJSON",
        "total_solicitados": cantidad,
        "nuevos_insertados": nuevos,
        "ya_existentes": ya_existentes,
    }

from sqlalchemy.orm import Session
from app.models.entidad_sql import ProductMaster


def obtener_perfil_dual(id_registro: int, db: Session) -> dict:
    doc_mongo = productos_collection.find_one({"_id": id_registro})
    reg_sql = db.query(ProductMaster).filter(ProductMaster.id == id_registro).first()

    if doc_mongo is None and reg_sql is None:
        raise LookupError(f"El registro con ID {id_registro} no existe en MongoDB ni en MySQL")

    datos_mongo = None
    if doc_mongo is not None:
        datos_mongo = dict(doc_mongo)
        if "_id" in datos_mongo:
            datos_mongo["_id"] = str(datos_mongo["_id"])

    datos_sql = None
    if reg_sql is not None:
        datos_sql = {
            col.name: getattr(reg_sql, col.name)
            for col in reg_sql.__table__.columns
        }