from typing import Union
import oracledb
from sqlalchemy import text

from database.connection import get_session
from core.exceptions import OrdemJaAtiva, OrdemNaoEncontrada, SemOrdemAtiva
from schemas.ordem import (
    OrdemResponse, OrdemActionResponse,
    ProximoItemResponse, SemItensResponse, IniciarOrdemRequest
)


async def listar_abertas() -> list[OrdemResponse]:
    async with get_session() as session:
        result = await session.execute(text("""
            SELECT id, numero, status, prioridade,
                   total_itens, itens_coletados, itens_pendentes,
                   NVL(pct_concluido, 0)
            FROM vw_ordens_painel
        """))
        rows = result.fetchall()

    return [
        OrdemResponse(
            id=r[0], numero=r[1], status=r[2], prioridade=r[3],
            total_itens=r[4], itens_coletados=r[5],
            itens_pendentes=r[6], pct_concluido=float(r[7])
        ) for r in rows
    ]


async def iniciar(req: IniciarOrdemRequest) -> OrdemActionResponse:
    async with get_session() as session:
        # Para stored procedures com OUT params no oracledb async,
        # acessamos a conexão raw do oracledb
        conn = await session.connection()
        raw_conn = conn.get_wrapped_connection()
        
        resultado_var = raw_conn.variable(oracledb.STRING)
        mensagem_var  = raw_conn.variable(oracledb.STRING)

        cursor = raw_conn.cursor()
        await cursor.callproc("sp_iniciar_ordem", [req.operador_id, req.ordem_id, resultado_var, mensagem_var])
        
        resultado = resultado_var.getvalue()
        mensagem  = mensagem_var.getvalue()
        await cursor.close()

    if resultado == 'ERRO':
        raise OrdemJaAtiva()

    return OrdemActionResponse(resultado=resultado, mensagem=mensagem)


async def pausar(ordem_id: int) -> OrdemActionResponse:
    async with get_session() as session:
        conn = await session.connection()
        raw_conn = conn.get_wrapped_connection()
        
        resultado_var = raw_conn.variable(oracledb.STRING)
        mensagem_var  = raw_conn.variable(oracledb.STRING)

        cursor = raw_conn.cursor()
        await cursor.callproc("sp_pausar_ordem", [ordem_id, resultado_var, mensagem_var])
        
        resultado = resultado_var.getvalue()
        mensagem  = mensagem_var.getvalue()
        await cursor.close()

    if resultado == 'ERRO':
        raise OrdemNaoEncontrada()

    return OrdemActionResponse(resultado=resultado, mensagem=mensagem)


async def proximo_item(operador_id: int) -> Union[ProximoItemResponse, SemItensResponse]:
    async with get_session() as session:
        result = await session.execute(text("""
            SELECT item_id, ordem_numero, sequencia, qtd_solicitada,
                   produto_codigo, produto_descricao, unidade,
                   rua, coluna, nivel, apartamento, endereco_completo,
                   setor, total_itens, itens_coletados
            FROM (
                SELECT * FROM vw_proximo_item
                WHERE operador_id = :operador_id
                ORDER BY sequencia
            )
            WHERE ROWNUM = 1
        """), {"operador_id": operador_id})
        row = result.fetchone()

    if not row:
        return SemItensResponse(mensagem="Todas as ordens concluídas. Bom trabalho!")

    return ProximoItemResponse(
        item_id=row[0],    ordem_numero=row[1],  sequencia=row[2],
        qtd_solicitada=row[3],
        produto_codigo=row[4],  produto_descricao=row[5],  unidade=row[6],
        rua=row[7],        coluna=row[8],         nivel=row[9],
        apartamento=row[10], endereco_completo=row[11],
        setor=row[12],     total_itens=row[13],   itens_coletados=row[14],
    )
