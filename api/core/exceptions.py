class AppException(Exception):
    """Base de todas as exceções do domínio."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class OperadorNaoEncontrado(AppException):
    def __init__(self, matricula: str):
        super().__init__(f"Operador não encontrado: {matricula}", 404)

class OperadorInativo(AppException):
    def __init__(self):
        super().__init__("Operador inativo.", 403)

class OrdemNaoEncontrada(AppException):
    def __init__(self):
        super().__init__("Ordem não encontrada.", 404)

class OrdemJaAtiva(AppException):
    def __init__(self):
        super().__init__("Operador já possui uma ordem em andamento.", 409)

class ItemNaoEncontrado(AppException):
    def __init__(self):
        super().__init__("Item não encontrado ou já coletado.", 404)

class CodigoIncorreto(AppException):
    def __init__(self, tentativa: int):
        super().__init__(f"Código incorreto. Tentativa {tentativa}.", 422)

class SemOrdemAtiva(AppException):
    def __init__(self):
        super().__init__("Operador não possui ordem em andamento.", 404)
