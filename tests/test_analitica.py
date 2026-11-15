
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.services import analitica_service, etl_service


# ==========================================
# PRUEBAS DE ANALITICA
# ==========================================

def test_analizar_columna_numerica(monkeypatch):
    valores = [100, 200, 300, None]

    resultado_consulta = MagicMock()
    resultado_consulta.scalars.return_value.all.return_value = valores

    db = MagicMock()
    db.execute.return_value = resultado_consulta

    resultado = analitica_service.analizar_columna("price", db)

    assert resultado["columna"] == "price"
    assert resultado["tipo"] == "numerica"
    assert resultado["min"] == 100
    assert resultado["max"] == 300
    assert resultado["promedio"] == 200
    assert resultado["mediana"] == 200
    assert resultado["nulos"] == 1


def test_analizar_columna_categorica():
    valores = ["tecnologia", "hogar", "tecnologia", None]

    resultado_consulta = MagicMock()
    resultado_consulta.scalars.return_value.all.return_value = valores

    db = MagicMock()
    db.execute.return_value = resultado_consulta

    resultado = analitica_service.analizar_columna("category", db)

    assert resultado["columna"] == "category"
    assert resultado["tipo"] == "categorica"
    assert resultado["valores_unicos"] == 2
    assert resultado["distribucion"] == {
        "tecnologia": 2,
        "hogar": 1,
    }
    assert resultado["valor_mas_comun"] == "tecnologia"
    assert resultado["nulos"] == 1


def test_analizar_columna_inexistente():
    db = MagicMock()

    with pytest.raises(ValueError, match="no válida"):
        analitica_service.analizar_columna("species", db)

    db.execute.assert_not_called()


def test_analizar_columna_booleana():
    valores = [1, 0, 1, None]

    resultado_consulta = MagicMock()
    resultado_consulta.scalars.return_value.all.return_value = valores

    db = MagicMock()
    db.execute.return_value = resultado_consulta

    resultado = analitica_service.analizar_columna(
        "es_stock_alto", db
    )

    assert resultado["tipo"] == "booleana"
    assert resultado["true"] == 2
    assert resultado["false"] == 1
    assert resultado["nulos"] == 1


# ==========================================
# PRUEBAS DE PERFIL DUAL
# ==========================================


def test_perfil_dual_sincronizado(monkeypatch):
    documento = {
        "_id": 101,
        "id": 101,
        "title": "Producto de prueba",
    }

    monkeypatch.setattr(
        etl_service.productos_collection,
        "find_one",
        lambda filtro: documento
    )

    # Crear un objeto que tenga las columnas reales del modelo
    registro_sql = MagicMock(spec=etl_service.ProductMaster)
    registro_sql.__table__ = etl_service.ProductMaster.__table__

    for columna in registro_sql.__table__.columns:
        setattr(
            registro_sql,
            columna.name,
            101 if columna.name == "id" else None
        )

    consulta = MagicMock()
    consulta.filter.return_value.first.return_value = registro_sql

    db = MagicMock()
    db.query.return_value = consulta

    resultado = etl_service.obtener_perfil_dual(101, db)

    assert resultado["estado_sincronizacion"] == "SINCRONIZADO"
    assert resultado["datos_staging_mongo"]["_id"] == "101"
    assert resultado["datos_analitica_sql"]["id"] == 101


def test_perfil_dual_solo_staging(monkeypatch):
    documento = {
        "_id": 102,
        "id": 102,
        "title": "Producto pendiente",
    }

    monkeypatch.setattr(
        etl_service.productos_collection,
        "find_one",
        lambda filtro: documento
    )

    consulta = MagicMock()
    consulta.filter.return_value.first.return_value = None

    db = MagicMock()
    db.query.return_value = consulta

    resultado = etl_service.obtener_perfil_dual(102, db)

    assert resultado["estado_sincronizacion"] == "SOLO_STAGING"
    assert resultado["datos_staging_mongo"]["_id"] == "102"
    assert resultado["datos_analitica_sql"] is None


def test_perfil_dual_registro_inexistente(monkeypatch):
    monkeypatch.setattr(
        etl_service.productos_collection,
        "find_one",
        lambda filtro: None
    )

    consulta = MagicMock()
    consulta.filter.return_value.first.return_value = None

    db = MagicMock()
    db.query.return_value = consulta

    with pytest.raises(LookupError, match="no existe"):
        etl_service.obtener_perfil_dual(999, db)
