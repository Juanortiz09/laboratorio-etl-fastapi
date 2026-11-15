
from types import SimpleNamespace

import pytest

from app.services import etl_service


def test_rechazar_cantidad_cero():
    with pytest.raises(ValueError, match="mayor a 0"):
        etl_service.extraer_datos_api(0)


def test_insertar_productos_nuevos(monkeypatch):
    productos = [
        {"id": 101, "title": "Producto de prueba"},
        {"id": 102, "title": "Otro producto"},
    ]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"products": productos}

    monkeypatch.setattr(
        etl_service.requests,
        "get",
        lambda *args, **kwargs: FakeResponse()
    )

    ids_insertados = []

    def fake_update_one(filtro, documento, upsert):
        ids_insertados.append(filtro["_id"])
        return SimpleNamespace(upserted_id=filtro["_id"])

    monkeypatch.setattr(
        etl_service.productos_collection,
        "update_one",
        fake_update_one
    )

    resultado = etl_service.extraer_datos_api(2)

    assert resultado["total_solicitados"] == 2
    assert resultado["nuevos_insertados"] == 2
    assert resultado["ya_existentes"] == 0
    assert ids_insertados == [101, 102]


def test_reconocer_productos_existentes(monkeypatch):
    productos = [
        {"id": 101, "title": "Producto existente"},
    ]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"products": productos}

    monkeypatch.setattr(
        etl_service.requests,
        "get",
        lambda *args, **kwargs: FakeResponse()
    )

    monkeypatch.setattr(
        etl_service.productos_collection,
        "update_one",
        lambda *args, **kwargs: SimpleNamespace(upserted_id=None)
    )

    resultado = etl_service.extraer_datos_api(1)

    assert resultado["total_solicitados"] == 1
    assert resultado["nuevos_insertados"] == 0
    assert resultado["ya_existentes"] == 1
