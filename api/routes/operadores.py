from fastapi import APIRouter
from schemas.operador import LoginRequest, OperadorResponse
from services import operador_service

router = APIRouter(prefix="/operadores", tags=["Operadores"])

@router.post("/login", response_model=OperadorResponse)
async def login(req: LoginRequest):
    return await operador_service.login(req.matricula)
