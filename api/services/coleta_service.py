import oracledb
from database.connection import get_session
from core.exceptions import ItemNaoEncontrado, CodigoIncorreto
from schemas.coleta import ConfirmarRequest, ConfirmarResponse


async def confirmar(req: ConfirmarRequest) -> ConfirmarResponse:
    async with get_session() as session:
        conn = await session.connection()
        raw_conn = conn.get_wrapped_connection()

        resultado_var        = raw_conn.variable(oracledb.STRING)
        mensagem_var         = raw_conn.variable(oracledb.STRING)
        comando_arduino_var  = raw_conn.variable(oracledb.STRING)
        tentativa_var        = raw_conn.variable(oracledb.NUMBER)

        cursor = raw_conn.cursor()
        await cursor.callproc("sp_confirmar_coleta", [
            req.item_id,
            req.operador_id,
            req.codigo_informado.strip().upper(),
            req.qtd_coletada,
            resultado_var,
            mensagem_var,
            comando_arduino_var,
            tentativa_var,
        ])

        res = resultado_var.getvalue()
        msg = mensagem_var.getvalue()
        cmd = comando_arduino_var.getvalue()
        ten = tentativa_var.getvalue()
        await cursor.close()

    if res == 'ERRO_SISTEMA':
        raise ItemNaoEncontrado()

    if res == 'ERRO_CODIGO':
        raise CodigoIncorreto(int(ten))

    return ConfirmarResponse(
        resultado=res,
        mensagem=msg,
        comando_arduino=cmd,
        tentativa=int(ten),
        sucesso=True,
    )
