
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import analitica_service


router = APIRouter(
    prefix="/api/v1/analitica",
    tags=["Analítica SQL"]
)


@router.get(
    "/columna/{nombre}",
    status_code=status.HTTP_200_OK,
    summary="Analizar estadísticamente una columna de MySQL",
)
def endpoint_analizar_columna(
    nombre: str,
    db: Session = Depends(get_db),
):
    try:
        return analitica_service.analizar_columna(nombre, db)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar la columna: {str(exc)}",
        )
