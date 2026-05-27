# AGENT.md — Pick By Voice
## Context for Gemini CLI

You are a senior Python developer continuing the **Pick By Voice Low Cost** project.
The database and FastAPI backend are **complete and must not be changed**.
Your job is to build the **Python voice client** that runs on an Android phone (or PC for testing).

---

## What is already done (do NOT touch)

### Database — OracleDB (running in Docker)
8 tables: `operadores`, `setores`, `enderecos`, `produtos`, `estoque`, `ordens`, `itens_ordem`, `log_coleta`
3 stored procedures: `sp_iniciar_ordem`, `sp_confirmar_coleta`, `sp_pausar_ordem`
3 views: `vw_proximo_item`, `vw_ordens_painel`, `vw_log_auditoria`

### API — FastAPI running at http://localhost:8000

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/operadores/login` | Auth by matricula → returns id, nome, ordens_pendentes |
| GET | `/api/ordens/abertas` | Lists open orders with progress |
| POST | `/api/ordens/iniciar` | Assigns operator to order |
| PATCH | `/api/ordens/{id}/pausar` | Pauses order |
| GET | `/api/coleta/proximo/{operador_id}` | Next pending item (no verification code) |
| POST | `/api/coleta/confirmar` | Validates spoken code, returns comando_arduino |
| GET | `/api/status` | Health check |

### Key API contract — POST /api/coleta/confirmar

Request:
```json
{ "item_id": 1, "operador_id": 1, "codigo_informado": "11", "qtd_coletada": 3 }
```

Response:
```json
{
  "resultado": "OK",
  "mensagem": "Item coletado. 3 restante(s).",
  "comando_arduino": "OK",
  "tentativa": 1,
  "sucesso": true
}
```
`comando_arduino` values: `OK` | `ERRO` | `FIM` — forward this directly to Arduino via Bluetooth.

---

## What you need to build

### File structure to create:

```
client/
├── main.py              ← entry point, picking loop
├── requirements.txt
├── .env
├── modules/
│   ├── stt.py           ← speech-to-text (Vosk, offline, pt-BR)
│   ├── tts.py           ← text-to-speech (pyttsx3, offline)
│   ├── api_client.py    ← HTTP wrapper around all API endpoints
│   └── bluetooth.py     ← send commands to Arduino via HC-05
```

---

## Module specs

### modules/stt.py
- Use **Vosk** library (offline, no internet required)
- Model path: `./model/` (user downloads vosk-model-small-pt-0.3)
- Load the model ONCE at module init (heavy operation)
- Function: `ouvir() -> str` — captures mic, returns recognized text
- Apply restricted vocabulary: numbers 0–99 + "ok" + "confirmar" + "feito" + "pular"
- Normalize output: strip, lowercase, remove punctuation

### modules/tts.py
- Use **pyttsx3** (offline)
- Configure Brazilian Portuguese voice if available
- Speed: 150 wpm
- Function: `falar(texto: str) -> None`

### modules/api_client.py
- Use **requests** library
- Base URL from `.env`: `API_URL=http://localhost:8000`
- Functions:
  - `login(matricula: str) -> dict`
  - `listar_ordens() -> list`
  - `iniciar_ordem(operador_id, ordem_id) -> dict`
  - `proximo_item(operador_id) -> dict`
  - `confirmar_coleta(item_id, operador_id, codigo, qtd) -> dict`
  - `pausar_ordem(ordem_id) -> dict`
- All functions raise `APIError` on non-2xx responses
- Timeout: 5 seconds on all requests

### modules/bluetooth.py
- Use **PyBluez** or **pyserial** (USB fallback)
- HC-05 MAC address or COM port from `.env`: `BT_ADDRESS=` or `BT_PORT=`
- Function: `enviar(comando: str) -> None` — appends `\n`, sends to Arduino
- Auto-reconnect on connection drop (retry 3x with 2s delay)
- If Bluetooth unavailable: log warning and continue (graceful degradation)

---

## main.py — Picking loop logic

```
1. Read operator matricula (input or env var OPERATOR_MATRICULA)
2. Call api_client.login(matricula)
3. falar(f"Bom dia, {nome}. Você tem {ordens_pendentes} ordens.")
4. Call api_client.listar_ordens() → pick highest priority AGUARDANDO order
5. Call api_client.iniciar_ordem(operador_id, ordem_id)
6. LOOP:
   a. item = api_client.proximo_item(operador_id)
   b. if item.get("fim"): break  ← SemItensResponse
   c. bluetooth.enviar(f"MSG:{item['rua']}{item['coluna']}{item['nivel']}{item['apartamento']}")
   d. falar(f"Vá para Rua {item['rua']}, Coluna {item['coluna']}, Nível {item['nivel']}, Apartamento {item['apartamento']}")
   e. falar(f"Produto: {item['produto_descricao']}. Quantidade: {item['qtd_solicitada']} {item['unidade']}")
   f. falar("Confirme o código da posição")
   g. codigo = stt.ouvir()  ← convert spoken number words to digits if needed
   h. result = api_client.confirmar_coleta(item['item_id'], operador_id, codigo, item['qtd_solicitada'])
   i. bluetooth.enviar(result['comando_arduino'])
   j. falar(result['mensagem'])
   k. if result['comando_arduino'] == 'ERRO': go back to step f (retry)
7. bluetooth.enviar("FIM")
8. falar("Coleta concluída. Dirija-se à expedição.")
```

---

## .env variables needed

```
API_URL=http://localhost:8000
BT_ADDRESS=              # HC-05 Bluetooth MAC (ex: 00:14:03:05:E5:B8)
BT_PORT=                 # or serial port if using USB (ex: /dev/ttyUSB0)
OPERATOR_MATRICULA=      # optional: skip login prompt
VOSK_MODEL_PATH=./model
```

---

## Important rules

1. `codigo_verificacao` never comes from the API. The operator reads it physically from the shelf and speaks it.
2. All STT input must be normalized before sending to API: `strip().upper()`
3. Convert spoken Portuguese number words to digits before sending:
   - "onze" → "11", "quarenta e sete" → "47", etc.
   - Use a simple dict or `num2words` reverse mapping
4. Bluetooth send must be non-blocking — if it fails, log and continue (don't crash the picking loop)
5. Load Vosk model only once at startup
6. All spoken text should be in Brazilian Portuguese
7. Handle `ERRO_CODIGO` (422) from API gracefully: don't crash, speak the error, retry

---

## Testing without Arduino

If `BT_ADDRESS` and `BT_PORT` are empty, `bluetooth.enviar()` should just `print(f"[ARDUINO] {comando}")` so the loop can be tested on PC without hardware.
