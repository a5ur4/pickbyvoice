from datetime import datetime
from pydantic import BaseModel, ConfigDict

class OperadorBase(BaseModel):
    nome: str
    matricula: str
    status: str = "ATIVO"

class LoginRequest(BaseModel):
    matricula: str

class OperadorResponse(OperadorBase):
    id: int
    ordens_pendentes: int = 0
    dt_cadastro: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
