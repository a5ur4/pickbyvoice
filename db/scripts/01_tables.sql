-- ============================================================
-- Script 01 — Tabelas
-- Executado automaticamente na 1ª inicialização do container.
--
-- Com gvenzl/oracle-xe:slim:
-- • O usuário APP_USER já foi criado pela imagem antes deste script rodar
-- • Os scripts rodam dentro do schema desse usuário automaticamente
-- • Não precisamos de ALTER SESSION, CREATE USER ou GRANT aqui
-- ============================================================


-- ------------------------------------------------------------
-- SETORES
-- Divisão física do armazém: Seco, Refrigerado, Pesado, etc.
-- Motivo: permite filtrar endereços por zona e organizar rotas.
-- ------------------------------------------------------------
CREATE TABLE setores (
    id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo    VARCHAR2(10)  NOT NULL,
    descricao VARCHAR2(100) NOT NULL,
    CONSTRAINT uq_setor_codigo UNIQUE (codigo)
);


-- ------------------------------------------------------------
-- OPERADORES
-- Colaboradores autorizados a realizar picking.
-- 'matricula' é o identificador usado no login por voz.
-- ------------------------------------------------------------
CREATE TABLE operadores (
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        VARCHAR2(100) NOT NULL,
    matricula   VARCHAR2(20)  NOT NULL,
    status      VARCHAR2(10)  DEFAULT 'ATIVO' NOT NULL,
    dt_cadastro DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_operador_matricula UNIQUE (matricula),
    CONSTRAINT ck_operador_status    CHECK (status IN ('ATIVO','INATIVO'))
);


-- ------------------------------------------------------------
-- ENDERECOS
-- Localização física de cada posição no armazém.
-- Estrutura de 4 níveis: rua > coluna > nivel > apartamento
--
-- codigo_verificacao: número de 2 dígitos afixado na prateleira.
-- O operador fala esse código para confirmar o local correto.
-- Nunca é retornado pela API — validado só dentro da procedure.
-- ------------------------------------------------------------
CREATE TABLE enderecos (
    id                  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rua                 VARCHAR2(5)  NOT NULL,
    coluna              VARCHAR2(5)  NOT NULL,
    nivel               VARCHAR2(5)  NOT NULL,
    apartamento         VARCHAR2(5)  NOT NULL,
    codigo_verificacao  VARCHAR2(10) NOT NULL,
    setor_id            NUMBER       NOT NULL,
    status              VARCHAR2(10) DEFAULT 'ATIVO' NOT NULL,
    CONSTRAINT fk_end_setor    FOREIGN KEY (setor_id) REFERENCES setores(id),
    CONSTRAINT uq_end_posicao  UNIQUE (rua, coluna, nivel, apartamento),
    CONSTRAINT ck_end_status   CHECK (status IN ('ATIVO','INATIVO','BLOQUEADO'))
);


-- ------------------------------------------------------------
-- PRODUTOS
-- Catálogo de itens que circulam pelo armazém.
-- ------------------------------------------------------------
CREATE TABLE produtos (
    id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo    VARCHAR2(30)  NOT NULL,
    descricao VARCHAR2(200) NOT NULL,
    unidade   VARCHAR2(10)  DEFAULT 'UN' NOT NULL,
    categoria VARCHAR2(50),
    ativo     VARCHAR2(1)   DEFAULT 'S' NOT NULL,
    CONSTRAINT uq_produto_codigo UNIQUE (codigo),
    CONSTRAINT ck_produto_ativo  CHECK (ativo IN ('S','N'))
);


-- ------------------------------------------------------------
-- ESTOQUE
-- Saldo de cada produto por endereço físico.
-- Um produto pode estar em múltiplos endereços.
-- ------------------------------------------------------------
CREATE TABLE estoque (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    produto_id      NUMBER NOT NULL,
    endereco_id     NUMBER NOT NULL,
    quantidade      NUMBER DEFAULT 0 NOT NULL,
    dt_atualizacao  DATE   DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_est_produto   FOREIGN KEY (produto_id)  REFERENCES produtos(id),
    CONSTRAINT fk_est_endereco  FOREIGN KEY (endereco_id) REFERENCES enderecos(id),
    CONSTRAINT uq_est_pos       UNIQUE (produto_id, endereco_id),
    CONSTRAINT ck_est_qtd       CHECK (quantidade >= 0)
);


-- ------------------------------------------------------------
-- ORDENS
-- Uma ordem de separação por operador de cada vez.
-- prioridade determina a ordem de exibição no painel WMS.
-- ------------------------------------------------------------
CREATE TABLE ordens (
    id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero       VARCHAR2(30) NOT NULL,
    operador_id  NUMBER,
    status       VARCHAR2(20) DEFAULT 'AGUARDANDO' NOT NULL,
    prioridade   VARCHAR2(10) DEFAULT 'NORMAL'     NOT NULL,
    dt_criacao   DATE         DEFAULT SYSDATE      NOT NULL,
    dt_inicio    DATE,
    dt_conclusao DATE,
    CONSTRAINT uq_ordem_numero     UNIQUE (numero),
    CONSTRAINT fk_ordem_operador   FOREIGN KEY (operador_id) REFERENCES operadores(id),
    CONSTRAINT ck_ordem_status     CHECK (status    IN ('AGUARDANDO','EM_ANDAMENTO','CONCLUIDA','CANCELADA','PAUSADA')),
    CONSTRAINT ck_ordem_prioridade CHECK (prioridade IN ('NORMAL','URGENTE','CRITICO'))
);


-- ------------------------------------------------------------
-- ITENS_ORDEM
-- Cada linha = um produto a coletar dentro de uma ordem.
-- 'sequencia' define a rota otimizada pelo armazém.
-- ------------------------------------------------------------
CREATE TABLE itens_ordem (
    id             NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ordem_id       NUMBER NOT NULL,
    produto_id     NUMBER NOT NULL,
    endereco_id    NUMBER NOT NULL,
    sequencia      NUMBER NOT NULL,
    qtd_solicitada NUMBER NOT NULL,
    qtd_coletada   NUMBER DEFAULT 0,
    status         VARCHAR2(20) DEFAULT 'PENDENTE' NOT NULL,
    CONSTRAINT fk_item_ordem    FOREIGN KEY (ordem_id)    REFERENCES ordens(id),
    CONSTRAINT fk_item_produto  FOREIGN KEY (produto_id)  REFERENCES produtos(id),
    CONSTRAINT fk_item_endereco FOREIGN KEY (endereco_id) REFERENCES enderecos(id),
    CONSTRAINT ck_item_status   CHECK (status IN ('PENDENTE','COLETADO','PULADO','ERRO')),
    CONSTRAINT ck_item_qtd      CHECK (qtd_solicitada > 0)
);


-- ------------------------------------------------------------
-- LOG_COLETA
-- Rastreabilidade completa: cada tentativa de confirmação
-- (certa ou errada) fica registrada permanentemente.
-- Serve para auditoria, KPIs de qualidade e treinamento.
-- ------------------------------------------------------------
CREATE TABLE log_coleta (
    id               NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id          NUMBER       NOT NULL,
    operador_id      NUMBER       NOT NULL,
    codigo_informado VARCHAR2(10) NOT NULL,
    sucesso          VARCHAR2(1)  NOT NULL,
    tentativa        NUMBER       DEFAULT 1 NOT NULL,
    dt_registro      DATE         DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_log_item     FOREIGN KEY (item_id)     REFERENCES itens_ordem(id),
    CONSTRAINT fk_log_operador FOREIGN KEY (operador_id) REFERENCES operadores(id),
    CONSTRAINT ck_log_sucesso  CHECK (sucesso IN ('S','N'))
);


-- ── Índices de performance ───────────────────────────────────
-- Query mais crítica: buscar próximo item pendente por operador
CREATE INDEX idx_item_ordem_status ON itens_ordem (ordem_id, status, sequencia);
CREATE INDEX idx_ordem_op_status   ON ordens      (operador_id, status);
CREATE INDEX idx_log_item          ON log_coleta  (item_id);
CREATE INDEX idx_est_produto       ON estoque     (produto_id);

COMMIT;
