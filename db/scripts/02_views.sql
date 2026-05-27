-- ============================================================
-- Script 02 — Views
-- Roda no schema do APP_USER (pickvoice) automaticamente.
-- ============================================================


-- ------------------------------------------------------------
-- VW_PROXIMO_ITEM
-- View principal da API: próximo item pendente por operador.
--
-- A API faz apenas: SELECT * FROM vw_proximo_item
--                   WHERE operador_id = ? AND ROWNUM = 1
--
-- Os contadores (total_itens, itens_coletados) usam window
-- functions para calcular o progresso sem subquery extra.
--
-- codigo_verificacao está na view mas NUNCA é exposto pela API.
-- Ele é usado internamente por sp_confirmar_coleta.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW vw_proximo_item AS
SELECT
    i.id                  AS item_id,
    o.id                  AS ordem_id,
    o.numero              AS ordem_numero,
    o.operador_id,
    i.sequencia,
    i.qtd_solicitada,
    p.codigo              AS produto_codigo,
    p.descricao           AS produto_descricao,
    p.unidade,
    e.rua,
    e.coluna,
    e.nivel,
    e.apartamento,
    e.rua || e.coluna || e.nivel || e.apartamento AS endereco_completo,
    e.codigo_verificacao,
    s.descricao           AS setor,
    COUNT(i2.id)          OVER (PARTITION BY o.id) AS total_itens,
    SUM(CASE WHEN i2.status = 'COLETADO' THEN 1 ELSE 0 END)
                          OVER (PARTITION BY o.id) AS itens_coletados
FROM itens_ordem i
JOIN ordens      o  ON o.id  = i.ordem_id
JOIN operadores  op ON op.id = o.operador_id
JOIN produtos    p  ON p.id  = i.produto_id
JOIN enderecos   e  ON e.id  = i.endereco_id
JOIN setores     s  ON s.id  = e.setor_id
JOIN itens_ordem i2 ON i2.ordem_id = i.ordem_id
WHERE i.status = 'PENDENTE'
  AND o.status = 'EM_ANDAMENTO';


-- ------------------------------------------------------------
-- VW_ORDENS_PAINEL
-- Painel WMS: ordens abertas com progresso em %.
-- Ordenada por prioridade (CRITICO primeiro).
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW vw_ordens_painel AS
SELECT
    o.id,
    o.numero,
    o.status,
    o.prioridade,
    o.dt_criacao,
    o.dt_inicio,
    NVL(op.nome,      '— sem operador —') AS operador_nome,
    NVL(op.matricula, '—')                AS operador_matricula,
    COUNT(i.id)                            AS total_itens,
    SUM(CASE WHEN i.status = 'COLETADO' THEN 1 ELSE 0 END) AS itens_coletados,
    SUM(CASE WHEN i.status = 'PENDENTE' THEN 1 ELSE 0 END) AS itens_pendentes,
    ROUND(
        SUM(CASE WHEN i.status = 'COLETADO' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(i.id), 0) * 100, 1
    ) AS pct_concluido
FROM ordens o
LEFT JOIN operadores  op ON op.id      = o.operador_id
LEFT JOIN itens_ordem i  ON i.ordem_id = o.id
WHERE o.status IN ('AGUARDANDO','EM_ANDAMENTO','PAUSADA')
GROUP BY
    o.id, o.numero, o.status, o.prioridade,
    o.dt_criacao, o.dt_inicio, op.nome, op.matricula
ORDER BY
    CASE o.prioridade WHEN 'CRITICO' THEN 1 WHEN 'URGENTE' THEN 2 ELSE 3 END,
    o.dt_criacao;


-- ------------------------------------------------------------
-- VW_LOG_AUDITORIA
-- Histórico legível de todas as coletas.
-- Útil para relatórios e identificar endereços problemáticos.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW vw_log_auditoria AS
SELECT
    l.id,
    l.dt_registro,
    op.matricula,
    op.nome              AS operador,
    o.numero             AS ordem,
    p.codigo             AS produto_codigo,
    p.descricao          AS produto,
    e.rua || e.coluna || e.nivel || e.apartamento AS endereco,
    l.codigo_informado,
    e.codigo_verificacao AS codigo_correto,
    l.sucesso,
    l.tentativa
FROM log_coleta  l
JOIN itens_ordem i  ON i.id  = l.item_id
JOIN ordens      o  ON o.id  = i.ordem_id
JOIN operadores  op ON op.id = l.operador_id
JOIN produtos    p  ON p.id  = i.produto_id
JOIN enderecos   e  ON e.id  = i.endereco_id
ORDER BY l.dt_registro DESC;

COMMIT;
