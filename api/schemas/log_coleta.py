from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LogColetaBase(BaseModel):
    item_id: int
    operador_id: int
    codigo_informado: str
    sucesso: str
    tentativa: int

class LogColetaCreate(LogColetaBase):
    pass

class LogColetaResponse(LogColetaBase):
    id: int
    dt_registro: datetime
    model_config = ConfigDict(from_attributes=True)
