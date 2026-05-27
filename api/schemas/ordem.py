from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OrdemResponse(BaseModel):
    id: int
    numero: str
    status: str
    prioridade: str
    total_itens: int
    itens_coletados: int
    itens_pendentes: int
    pct_concluido: float
    dt_criacao: datetime | None = None
    dt_inicio: datetime | None = None
    dt_conclusao: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class IniciarOrdemRequest(BaseModel):
    operador_id: int
    ordem_id: int


class OrdemActionResponse(BaseModel):
    resultado: str
    mensagem: str


# Retornado pela rota GET /coleta/proximo/{operador_id}
# codigo_verificacao NUNCA aparece aqui
class ProximoItemResponse(BaseModel):
    item_id: int
    ordem_numero: str
    sequencia: int
    total_itens: int
    itens_coletados: int
    produto_codigo: str
    produto_descricao: str
    unidade: str
    qtd_solicitada: int
    rua: str
    coluna: str
    nivel: str
    apartamento: str
    endereco_completo: str
    setor: str


class SemItensResponse(BaseModel):
    fim: bool = True
    mensagem: str
