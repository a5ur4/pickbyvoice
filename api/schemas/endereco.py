from pydantic import BaseModel, ConfigDict

class EnderecoBase(BaseModel):
    rua: str
    coluna: str
    nivel: str
    apartamento: str
    setor_id: int
    status: str = "ATIVO"

class EnderecoCreate(EnderecoBase):
    codigo_verificacao: str

class EnderecoResponse(EnderecoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
