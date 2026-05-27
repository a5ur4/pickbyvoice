from pydantic import BaseModel


class ConfirmarRequest(BaseModel):
    item_id: int
    operador_id: int
    codigo_informado: str
    qtd_coletada: int


class ConfirmarResponse(BaseModel):
    resultado: str          # OK | ERRO_CODIGO | ERRO_SISTEMA
    mensagem: str
    comando_arduino: str    # OK | ERRO | FIM  → repassado via Bluetooth
    tentativa: int
    sucesso: bool
    model_config = ConfigDict(from_attributes=True)
