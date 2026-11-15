from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import etl_service
from app.views.schemas import ResetResponse

router = APIRouter(prefix="/api/v1/etl", tags=["ETL Pipeline"])


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



from fastapi import HTTPException, status
from app.views.schemas import ExtraerRequest, ExtraerResponse
from app.services import etl_service


@router.post("/extraer", response_model=ExtraerResponse, status_code=status.HTTP_201_CREATED)
def endpoint_extraer(payload: ExtraerRequest):
    try:
        return etl_service.extraer_datos_api(payload.cantidad)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en extracción: {str(exc)}")