
from datetime import date, datetime
from collections import Counter
from statistics import mean, median, stdev

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
)

from app.models.entidad_sql import ProductMaster


def analizar_columna(nombre: str, db: Session) -> dict:
    # Obtener las columnas válidas del modelo SQL
    columnas = ProductMaster.__table__.columns
    columnas_validas = list(columnas.keys())

    # Validar que la columna exista
    if nombre not in columnas_validas:
        raise ValueError(
            f"Columna '{nombre}' no válida. "
            f"Columnas disponibles: {columnas_validas}"
        )

    columna = columnas[nombre]

    # Consultar únicamente la columna solicitada
    valores = db.execute(
        select(columna)
    ).scalars().all()

    nulos = sum(valor is None for valor in valores)
    valores_validos = [
        valor for valor in valores if valor is not None
    ]

    tipo_sql = columna.type

    # 1. Detectar fechas
    if isinstance(tipo_sql, (Date, DateTime)):
        fechas = [
            valor.date() if isinstance(valor, datetime) else valor
            for valor in valores_validos
        ]

        if not fechas:
            return {
                "columna": nombre,
                "tipo": "fecha",
                "min": None,
                "max": None,
                "rango_dias": None,
                "nulos": nulos,
            }

        fecha_min = min(fechas)
        fecha_max = max(fechas)

        return {
            "columna": nombre,
            "tipo": "fecha",
            "min": fecha_min.isoformat(),
            "max": fecha_max.isoformat(),
            "rango_dias": (fecha_max - fecha_min).days,
            "nulos": nulos,
        }

    # 2. Detectar booleanos declarados en SQLAlchemy
    if isinstance(tipo_sql, Boolean):
        return {
            "columna": nombre,
            "tipo": "booleana",
            "true": sum(bool(valor) for valor in valores_validos),
            "false": sum(not bool(valor) for valor in valores_validos),
            "nulos": nulos,
        }

    # 3. Detectar columnas numéricas
    if isinstance(tipo_sql, (Integer, Float, Numeric)):
        # MySQL puede almacenar booleanos como 0 y 1
        if valores_validos and all(
            valor in (0, 1) for valor in valores_validos
        ):
            return {
                "columna": nombre,
                "tipo": "booleana",
                "true": sum(valor == 1 for valor in valores_validos),
                "false": sum(valor == 0 for valor in valores_validos),
                "nulos": nulos,
            }

        numeros = [float(valor) for valor in valores_validos]

        if not numeros:
            return {
                "columna": nombre,
                "tipo": "numerica",
                "min": None,
                "max": None,
                "promedio": None,
                "mediana": None,
                "desviacion_std": None,
                "nulos": nulos,
            }

        return {
            "columna": nombre,
            "tipo": "numerica",
            "min": min(numeros),
            "max": max(numeros),
            "promedio": mean(numeros),
            "mediana": median(numeros),
            "desviacion_std": stdev(numeros) if len(numeros) > 1 else 0,
            "nulos": nulos,
        }

    # 4. Detectar columnas de texto
    if isinstance(tipo_sql, (String, Text)):
        distribucion = Counter(valores_validos)
        valores_unicos = len(distribucion)

        # Si todos los valores son distintos, es texto libre
        if valores_unicos == len(valores_validos):
            return {
                "columna": nombre,
                "tipo": "texto",
                "valores_unicos": valores_unicos,
                "nulos": nulos,
            }

        valor_mas_comun = (
            distribucion.most_common(1)[0][0]
            if distribucion else None
        )

        return {
            "columna": nombre,
            "tipo": "categorica",
            "valores_unicos": valores_unicos,
            "distribucion": dict(distribucion),
            "valor_mas_comun": valor_mas_comun,
            "nulos": nulos,
        }

    raise ValueError(
        f"El tipo de dato de la columna '{nombre}' no está soportado."
    )
