from pydantic import BaseModel, ConfigDict

class SetorBase(BaseModel):
    codigo: str
    descricao: str

class SetorCreate(SetorBase):
    pass

class SetorResponse(SetorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
