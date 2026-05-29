import oracledb
from database.connection import get_session
from core.exceptions import ItemNaoEncontrado, CodigoIncorreto
from schemas.coleta import ConfirmarRequest, ConfirmarResponse


async def confirmar(req: ConfirmarRequest) -> ConfirmarResponse:
    async with get_session() as session:
        conn = await session.connection()
        adapt = await conn.get_raw_connection()
        raw_conn = adapt.dbapi_connection.driver_connection

        async with raw_conn.cursor() as cursor:
            cursor.setinputsizes(
                None, None, None, None, 
                oracledb.STRING, oracledb.STRING, oracledb.STRING, oracledb.NUMBER
            )
            
            res_list = await cursor.callproc("sp_confirmar_coleta", [
                req.item_id,
                req.operador_id,
                req.codigo_informado.strip().upper(),
                req.qtd_coletada,
                " " * 100,  # resultado
                " " * 500,  # mensagem
                " " * 100,  # comando_arduino
                0           # tentativa
            ])

            res = res_list[4]
            msg = res_list[5]
            cmd = res_list[6]
            ten = res_list[7]

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
