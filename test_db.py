import asyncio
import sys
import os

# Adiciona o diretório da API ao path para poder importar os módulos
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), 'api')))

from api.database.connection import init_pool, close_pool, get_session
from sqlalchemy import text

async def test_connection():
    print("Iniciando teste de conexão assíncrona com Oracle...")
    try:
        # Inicializa o pool
        await init_pool()
        print("Pool inicializado com sucesso.")

        # Testa uma sessão
        async with get_session() as session:
            print("Sessão aberta.")
            result = await session.execute(text("SELECT 'Conexão OK' FROM DUAL"))
            row = result.fetchone()
            print(f"Resultado da consulta: {row[0]}")

        print("Teste concluído com sucesso!")
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Fecha o pool
        await close_pool()
        print("Pool fechado.")

if __name__ == "__main__":
    asyncio.run(test_connection())
