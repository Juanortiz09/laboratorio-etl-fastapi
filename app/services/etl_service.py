
import requests
import pandas as pd

from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import productos_collection
from app.models.entidad_sql import ProductMaster


# ==========================================
# 1. ENDPOINT RESET
# ==========================================

def reset_datos(db: Session) -> dict:
    # Eliminar documentos de MongoDB
    resultado_mongo = productos_collection.delete_many({})
    docs_eliminados = resultado_mongo.deleted_count

    # Contar registros y vaciar tabla MySQL
    registros_sql = db.query(ProductMaster).count()

    db.execute(text("TRUNCATE TABLE productos_master"))
    db.commit()

    return {
        "mensaje": "Bases de datos MongoDB y MySQL reiniciadas correctamente",
        "documentos_eliminados_mongo": docs_eliminados,
        "registros_eliminados_sql": registros_sql,
    }


# ==========================================
# 2. ENDPOINT EXTRACCION
# ==========================================

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
            settings.DUMMYJSON_URL,
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


# ==========================================
# 3. ENDPOINT PERFIL DUAL
# ==========================================

def obtener_perfil_dual(id_registro: int, db: Session) -> dict:

    # Consultar MongoDB
    doc_mongo = productos_collection.find_one({"_id": id_registro})

    # Consultar MySQL
    reg_sql = (
        db.query(ProductMaster)
        .filter(ProductMaster.id == id_registro)
        .first()
    )

    if doc_mongo is None and reg_sql is None:
        raise LookupError(
            f"El registro con ID {id_registro} "
            "no existe en MongoDB ni en MySQL"
        )

    # Preparar documento MongoDB
    datos_mongo = None

    if doc_mongo is not None:
        datos_mongo = dict(doc_mongo)
        datos_mongo["_id"] = str(datos_mongo["_id"])

    # Preparar registro MySQL
    datos_sql = None

    if reg_sql is not None:
        datos_sql = {
            col.name: getattr(reg_sql, col.name)
            for col in reg_sql.__table__.columns
        }

    # Determinar estado de sincronización
    if datos_mongo is not None and datos_sql is not None:
        estado = "SINCRONIZADO"
        mensaje = (
            "El registro existe tanto en Staging (MongoDB) "
            "como en Analítica (MySQL)"
        )

    elif datos_mongo is not None:
        estado = "SOLO_STAGING"
        mensaje = (
            "El registro existe únicamente en Staging (MongoDB); "
            "falta transformar a MySQL"
        )

    else:
        estado = "SOLO_ANALITICA"
        mensaje = (
            "El registro existe únicamente en Analítica (MySQL)"
        )

    return {
        "id": id_registro,
        "estado_sincronizacion": estado,
        "mensaje": mensaje,
        "datos_staging_mongo": datos_mongo,
        "datos_analitica_sql": datos_sql,
    }

# ==========================================
# 4. TRANSFORMACION Y CARGA A MYSQL
# ==========================================

def transformar_y_cargar(db: Session) -> dict:

    # 1. Leer documentos originales de MongoDB
    documentos = list(productos_collection.find({}))

    if not documentos:
        raise ValueError(
            "No hay documentos en MongoDB para transformar. "
            "Primero ejecuta el endpoint de extracción."
        )

    # 2. Aplanar los documentos anidados con Pandas
    df = pd.json_normalize(documentos, sep="_")

    # 3. Recuperar el identificador original
    if "id" not in df.columns:
        df["id"] = df["_id"]

    # 4. Renombrar columnas para adaptarlas a MySQL
    df = df.rename(columns={
        "discountPercentage": "discount_percentage",
        "dimensions_width": "width",
        "meta_createdAt": "created_at",
    })

    # 5. Preparar las columnas de texto
    for columna in ["title", "category", "brand"]:
        if columna not in df.columns:
            df[columna] = "N/A"

        df[columna] = df[columna].fillna("N/A").astype(str)

    # 6. Convertir columnas numéricas
    columnas_numericas = [
        "id",
        "price",
        "discount_percentage",
        "rating",
        "stock",
        "width",
    ]

    for columna in columnas_numericas:
        if columna not in df.columns:
            df[columna] = None

        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    # 7. Convertir fechas
    if "created_at" not in df.columns:
        df["created_at"] = None

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
        utc=True
    ).dt.tz_convert(None)

    # 8. Crear columna derivada
    # Se considera stock alto cuando supera 50 unidades.
    df["es_stock_alto"] = df["stock"].apply(
        lambda valor: False if pd.isna(valor) else valor > 50
    )

    # 9. Preparar registros compatibles con SQLAlchemy
    columnas_sql = [
        "id",
        "title",
        "category",
        "brand",
        "price",
        "discount_percentage",
        "rating",
        "stock",
        "width",
        "created_at",
        "es_stock_alto",
    ]

    registros = []

    for _, fila in df.iterrows():
        registro = {}

        for columna in columnas_sql:
            valor = fila[columna]

            if pd.isna(valor):
                valor = None
            elif columna == "id":
                valor = int(valor)
            elif columna == "stock":
                valor = int(valor)
            elif columna in [
                "price",
                "discount_percentage",
                "rating",
                "width",
            ]:
                valor = float(valor)
            elif columna == "created_at":
                valor = valor.to_pydatetime()
            elif columna == "es_stock_alto":
                valor = bool(valor)

            registro[columna] = valor

        registros.append(registro)

    # 10. Cargar en MySQL mediante UPSERT
    # Si el ID ya existe, actualiza sus datos.
    try:
        sentencia = mysql_insert(ProductMaster).values(registros)

        actualizaciones = {
            columna: sentencia.inserted[columna]
            for columna in columnas_sql
            if columna != "id"
        }

        sentencia = sentencia.on_duplicate_key_update(
            **actualizaciones
        )

        db.execute(sentencia)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "mensaje": "Transformación y carga completadas correctamente",
        "documentos_procesados": len(documentos),
        "registros_cargados_sql": len(registros),
    }
