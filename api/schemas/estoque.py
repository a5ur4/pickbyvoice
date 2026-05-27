from datetime import datetime
from pydantic import BaseModel, ConfigDict

class EstoqueBase(BaseModel):
    produto_id: int
    endereco_id: int
    quantidade: int

class EstoqueCreate(EstoqueBase):
    pass

class EstoqueResponse(EstoqueBase):
    id: int
    dt_atualizacao: datetime
    model_config = ConfigDict(from_attributes=True)
