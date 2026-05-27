from pydantic import BaseModel, ConfigDict

class ProdutoBase(BaseModel):
    codigo: str
    descricao: str
    unidade: str = "UN"
    categoria: str | None = None
    ativo: str = "S"

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
