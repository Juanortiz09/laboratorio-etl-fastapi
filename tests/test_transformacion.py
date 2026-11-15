
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.services import etl_service


def test_error_si_mongo_esta_vacio(monkeypatch):
    monkeypatch.setattr(
        etl_service.productos_collection,
        "find",
        lambda filtro: []
    )

    db = MagicMock()

    with pytest.raises(ValueError, match="No hay documentos en MongoDB"):
        etl_service.transformar_y_cargar(db)

    db.execute.assert_not_called()
    db.commit.assert_not_called()


def test_transformar_y_cargar_correctamente(monkeypatch):
    documentos = [
        {
            "_id": 101,
            "id": 101,
            "title": "Producto de prueba",
            "category": "tecnologia",
            "brand": "Marca X",
            "price": 100,
            "discountPercentage": 10,
            "rating": 4.5,
            "stock": 80,
            "dimensions": {"width": 15},
            "meta": {"createdAt": "2025-01-15T10:00:00Z"},
        }
    ]

    monkeypatch.setattr(
        etl_service.productos_collection,
        "find",
        lambda filtro: documentos
    )

    db = MagicMock()

    resultado = etl_service.transformar_y_cargar(db)

    assert resultado["documentos_procesados"] == 1
    assert resultado["registros_cargados_sql"] == 1
    assert resultado["mensaje"] == (
        "Transformación y carga completadas correctamente"
    )

    db.execute.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_rollback_si_falla_la_carga(monkeypatch):
    documentos = [
        {
            "_id": 102,
            "id": 102,
            "title": "Producto de prueba",
            "category": "tecnologia",
            "brand": "Marca X",
            "price": 200,
            "discountPercentage": 5,
            "rating": 4.0,
            "stock": 30,
            "dimensions": {"width": 20},
            "meta": {"createdAt": "2025-01-15T10:00:00Z"},
        }
    ]

    monkeypatch.setattr(
        etl_service.productos_collection,
        "find",
        lambda filtro: documentos
    )

    db = MagicMock()
    db.execute.side_effect = Exception("Error simulado en MySQL")

    with pytest.raises(Exception, match="Error simulado en MySQL"):
        etl_service.transformar_y_cargar(db)

    db.rollback.assert_called_once()
    db.commit.assert_not_called()
