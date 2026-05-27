from sqlalchemy import text
from database.connection import get_session
from core.exceptions import OperadorNaoEncontrado, OperadorInativo
from schemas.operador import OperadorResponse


async def login(matricula: str) -> OperadorResponse:
    async with get_session() as session:
        # Busca o operador pela matrícula
        result = await session.execute(
            text("SELECT id, nome, matricula, status FROM operadores WHERE matricula = :matricula"),
            {"matricula": matricula.upper().strip()}
        )
        row = result.fetchone()

    if not row:
        raise OperadorNaoEncontrado(matricula)

    op_id, nome, mat, status = row

    if status != 'ATIVO':
        raise OperadorInativo()

    # Conta ordens ativas do operador
    async with get_session() as session:
        result = await session.execute(
            text("SELECT COUNT(*) FROM ordens WHERE operador_id = :op_id AND status IN ('EM_ANDAMENTO','PAUSADA')"),
            {"op_id": op_id}
        )
        (pendentes,) = result.fetchone()

    return OperadorResponse(
        id=op_id,
        nome=nome,
        matricula=mat,
        ordens_pendentes=pendentes,
    )
