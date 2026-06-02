import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_URL", "http://localhost:8000/api")
if not BASE_URL.endswith("/api"):
    BASE_URL += "/api"

class APIError(Exception):
    pass

def login(matricula: str) -> dict:
    resp = requests.post(f"{BASE_URL}/operadores/login", json={"matricula": matricula}, timeout=5)
    if not resp.ok:
        raise APIError(f"Erro no login: {resp.text}")
    return resp.json()

def listar_ordens() -> list:
    resp = requests.get(f"{BASE_URL}/ordens/abertas", timeout=5)
    if not resp.ok:
        raise APIError(f"Erro ao listar ordens: {resp.text}")
    return resp.json()

def iniciar_ordem(operador_id: int, ordem_id: int) -> dict:
    resp = requests.post(f"{BASE_URL}/ordens/iniciar", json={"operador_id": operador_id, "ordem_id": ordem_id}, timeout=5)
    if not resp.ok:
        raise APIError(f"Erro ao iniciar ordem: {resp.text}")
    return resp.json()

def proximo_item(operador_id: int) -> dict:
    resp = requests.get(f"{BASE_URL}/coleta/proximo/{operador_id}", timeout=5)
    if not resp.ok:
        raise APIError(f"Erro ao buscar próximo item: {resp.text}")
    return resp.json()

def confirmar_coleta(item_id: int, operador_id: int, codigo: str, qtd: int) -> dict:
    payload = {
        "item_id": item_id,
        "operador_id": operador_id,
        "codigo_informado": codigo,
        "qtd_coletada": qtd
    }
    resp = requests.post(f"{BASE_URL}/coleta/confirmar", json=payload, timeout=5)
    
    # 422 Unprocessable Entity can occur on wrong code (ERRO_CODIGO)
    # We should return it to handle it gracefully in the loop
    if resp.status_code == 422:
        return resp.json()
    elif not resp.ok:
        raise APIError(f"Erro ao confirmar coleta: {resp.text}")
        
    return resp.json()

def pausar_ordem(ordem_id: int) -> dict:
    resp = requests.patch(f"{BASE_URL}/ordens/{ordem_id}/pausar", timeout=5)
    if not resp.ok:
        raise APIError(f"Erro ao pausar ordem: {resp.text}")
    return resp.json()
