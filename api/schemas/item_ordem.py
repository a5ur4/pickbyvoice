from pydantic import BaseModel, ConfigDict

class ItemOrdemBase(BaseModel):
    ordem_id: int
    produto_id: int
    endereco_id: int
    sequencia: int
    qtd_solicitada: int
    qtd_coletada: int = 0
    status: str = "PENDENTE"

class ItemOrdemCreate(ItemOrdemBase):
    pass

class ItemOrdemResponse(ItemOrdemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
