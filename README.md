# Pick By Voice — Low Cost 🎙️📦

Sistema de separação de pedidos (Picking) por comandos de voz de baixo custo, integrado com **Oracle Database**, **FastAPI** e **Arduino**.

Este projeto permite que operadores de armazém realizem a coleta de itens de forma "hands-free", recebendo instruções via áudio e confirmando localizações/quantidades por voz, com feedback visual e sonoro através de um módulo Arduino conectado via Bluetooth.

---

## 🏗️ Arquitetura do Sistema

O ecossistema é dividido em três camadas principais:

1.  **Backend (API + DB)**: Centraliza as regras de negócio, controle de estoque e ordens de serviço.
2.  **Cliente de Voz (Python)**: Roda em um dispositivo móvel (Android/PC) e faz a ponte entre o operador (STT/TTS) e a API.
3.  **Interface de Hardware (Arduino)**: Fornece sinais visuais (LED/LCD) e sonoros (Buzzer) baseados no status da coleta.

---

## 📂 Estrutura do Projeto

```text
pickbyvoice/
├── api/                # Backend FastAPI (Assíncrono)
│   ├── core/           # Configurações e Exceções
│   ├── database/       # Conexão e Pool (SQLAlchemy + OracleDB)
│   ├── migrations/     # Versionamento de banco (Alembic)
│   ├── models/         # Modelos SQLAlchemy 2.0 (Mapped/Identity)
│   ├── routes/         # Endpoints da API (Operadores, Ordens, Coleta)
│   ├── schemas/        # Schemas Pydantic (Validação de dados)
│   └── services/       # Lógica de negócio e Stored Procedures
├── arduino/            # Firmware C++ para o Arduino Uno
├── db/                 # Scripts SQL originais (Tabelas, Views, Procs, Seed)
├── .env                # Variáveis de ambiente (DB, API)
└── README.md           # Este arquivo
```

---

## 🛠️ Tecnologias Utilizadas

*   **Linguagens**: Python 3.12+ (Backend/Client) e C++ (Arduino).
*   **Banco de Dados**: Oracle Database XE (rodando em Docker).
*   **ORM**: SQLAlchemy 2.0 (Modo Assíncrono).
*   **Migrations**: Alembic.
*   **Framework Web**: FastAPI (Uvicorn).
*   **Voz**: Vosk (Speech-to-Text Offline) e pyttsx3 (Text-to-Speech).

---

## 🚀 Como Rodar o Projeto

### 1. Banco de Dados (Oracle XE)
Certifique-se de ter o Docker instalado e rode o container:
```bash
docker-compose up -d
```
A imagem `gvenzl/oracle-xe` inicializará o banco e criará o usuário configurado no `.env`.

### 2. Preparar o Ambiente Python
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
```

### 3. Migrações e Dados Iniciais
Aplique as migrações para criar as tabelas e execute o seed se necessário:
```bash
cd api
export ORACLE_DSN="localhost:1521?service_name=XEPDB1"
alembic upgrade head
```

### 4. Executar a API
Na raiz do projeto:
```bash
source .venv/bin/activate
export ORACLE_DSN="localhost:1521?service_name=XEPDB1"
fastapi run api/main.py
```
Acesse `http://localhost:8000/docs` para ver a documentação interativa (Swagger).

### 5. Arduino
*   Carregue o arquivo `arduino/pick_by_voice.ino` no seu Arduino Uno.
*   Conecte um módulo Bluetooth (ex: HC-05) aos pinos de Serial.
*   Pinos padrão: LED OK (8), LED ERRO (9), Buzzer (10), LCD I2C (0x27).

---

## 🗣️ Funcionamento do Pick By Voice

1.  **Login**: O operador informa sua matrícula via voz.
2.  **Início**: O sistema atribui a ordem de maior prioridade ao operador.
3.  **Instrução**: A voz sintetizada diz o endereço (Rua, Coluna, Nível) e o produto.
4.  **Ação no Arduino**: O endereço é exibido no LCD e o LED de alerta acende.
5.  **Confirmação**: O operador fala o código de verificação presente na prateleira.
6.  **Validação**: A API valida o código. Se correto, o Arduino apita e acende o LED verde. Se errado, acende o LED vermelho e solicita nova tentativa.
7.  **Finalização**: Ao concluir todos os itens, o sistema guia o operador para a expedição.

---

## 🛡️ Decisões Técnicas
*   **Async Oracle**: Utilizamos `oracledb_async` para garantir que a API não bloqueie durante chamadas de banco pesadas ou execuções de stored procedures.
*   **Identity Columns**: Utilizamos o recurso nativo do Oracle 12c+ (`GENERATED AS IDENTITY`) mapeado no SQLAlchemy para garantir chaves primárias seguras e eficientes.
*   **Alembic Async**: O script de migração foi customizado para utilizar o driver assíncrono, mantendo a consistência com o restante da aplicação.
