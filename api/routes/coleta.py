from typing import Union
from fastapi import APIRouter
from schemas.coleta import ConfirmarRequest, ConfirmarResponse
from schemas.ordem import ProximoItemResponse, SemItensResponse
from services import ordem_service, coleta_service

router = APIRouter(prefix="/coleta", tags=["Coleta"])

@router.get("/proximo/{operador_id}", response_model=Union[ProximoItemResponse, SemItensResponse])
async def proximo(operador_id: int):
    return await ordem_service.proximo_item(operador_id)

@router.post("/confirmar", response_model=ConfirmarResponse)
async def confirmar(req: ConfirmarRequest):
    return await coleta_service.confirmar(req)
