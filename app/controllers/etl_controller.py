
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import etl_service
from app.views.schemas import (
    ResetResponse,
    ExtraerRequest,
    ExtraerResponse,
    PerfilDualResponse,
    TransformarResponse,
)


router = APIRouter(
    prefix="/api/v1/etl",
    tags=["ETL Pipeline"]
)


# ==========================================
# 1. RESET DE BASES DE DATOS
# ==========================================

@router.delete(
    "/reset",
    response_model=ResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Reiniciar bases de datos (MongoDB y MySQL)",
)
def reset_pipeline(db: Session = Depends(get_db)):
    try:
        return etl_service.reset_datos(db)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reiniciar las bases de datos: {str(e)}",
        )


# ==========================================
# 2. EXTRACCION DE DATOS
# ==========================================

@router.post(
    "/extraer",
    response_model=ExtraerResponse,
    status_code=status.HTTP_201_CREATED,
)
def endpoint_extraer(payload: ExtraerRequest):
    try:
        return etl_service.extraer_datos_api(payload.cantidad)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en extracción: {str(exc)}",
        )


# ==========================================
# 3. PERFIL DUAL MONGODB Y MYSQL
# ==========================================

@router.get(
    "/perfil/{id}",
    response_model=PerfilDualResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar perfil dual de un producto (MongoDB vs MySQL)",
)
def endpoint_perfil_dual(id: int, db: Session = Depends(get_db)):
    try:
        return etl_service.obtener_perfil_dual(id, db)

    except LookupError as le:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(le),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar perfil dual: {str(exc)}",
        )


# ==========================================
# 4. TRANSFORMACION Y CARGA A MYSQL
# ==========================================

@router.post(
    "/transformar",
    response_model=TransformarResponse,
    status_code=status.HTTP_200_OK,
    summary="Transformar datos de MongoDB y cargarlos en MySQL",
)
def endpoint_transformar(db: Session = Depends(get_db)):
    try:
        return etl_service.transformar_y_cargar(db)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en transformación y carga: {str(exc)}",
        )
