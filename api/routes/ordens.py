from fastapi import APIRouter
from schemas.ordem import IniciarOrdemRequest, OrdemActionResponse, OrdemResponse
from services import ordem_service

router = APIRouter(prefix="/ordens", tags=["Ordens"])

@router.get("/abertas", response_model=list[OrdemResponse])
async def listar_abertas():
    return await ordem_service.listar_abertas()

@router.post("/iniciar", response_model=OrdemActionResponse)
async def iniciar(req: IniciarOrdemRequest):
    return await ordem_service.iniciar(req)

@router.patch("/{ordem_id}/pausar", response_model=OrdemActionResponse)
async def pausar(ordem_id: int):
    return await ordem_service.pausar(ordem_id)
