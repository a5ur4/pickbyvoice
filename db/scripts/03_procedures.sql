-- ============================================================
-- Script 03 — Stored Procedures
-- Roda no schema do APP_USER (pickvoice) automaticamente.
-- ============================================================


-- ------------------------------------------------------------
-- SP_INICIAR_ORDEM
-- Associa um operador a uma ordem e a coloca EM_ANDAMENTO.
-- Regra: operador só pode ter UMA ordem ativa por vez.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_iniciar_ordem (
    p_operador_id IN  NUMBER,
    p_ordem_id    IN  NUMBER,
    p_resultado   OUT VARCHAR2,
    p_mensagem    OUT VARCHAR2
) AS
    v_ativas NUMBER;
    v_status VARCHAR2(20);
BEGIN
    -- Garante que o operador não tem outra ordem ativa
    SELECT COUNT(*) INTO v_ativas
    FROM ordens
    WHERE operador_id = p_operador_id
      AND status = 'EM_ANDAMENTO';

    IF v_ativas > 0 THEN
        p_resultado := 'ERRO';
        p_mensagem  := 'Operador já possui uma ordem em andamento.';
        RETURN;
    END IF;

    -- Verifica se a ordem pode ser iniciada
    SELECT status INTO v_status
    FROM ordens WHERE id = p_ordem_id;

    IF v_status NOT IN ('AGUARDANDO', 'PAUSADA') THEN
        p_resultado := 'ERRO';
        p_mensagem  := 'Ordem indisponível. Status atual: ' || v_status;
        RETURN;
    END IF;

    UPDATE ordens
    SET operador_id = p_operador_id,
        status      = 'EM_ANDAMENTO',
        dt_inicio   = SYSDATE
    WHERE id = p_ordem_id;

    COMMIT;
    p_resultado := 'OK';
    p_mensagem  := 'Ordem iniciada com sucesso.';

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_resultado := 'ERRO';
        p_mensagem  := 'Ordem não encontrada: ' || p_ordem_id;
    WHEN OTHERS THEN
        ROLLBACK;
        p_resultado := 'ERRO';
        p_mensagem  := SQLERRM;
END sp_iniciar_ordem;
/


-- ------------------------------------------------------------
-- SP_CONFIRMAR_COLETA
-- Chamada a cada vez que o operador fala o código.
--
-- Fluxo:
-- 1. Busca o código correto do endereço
-- 2. Registra a tentativa no log (sempre, acerto ou erro)
-- 3. Compara os códigos (case-insensitive, trim)
-- 4. Erro → retorna ERRO_CODIGO, arduino pisca vermelho
-- 5. Acerto → marca item COLETADO
-- 6. Último item → conclui a ordem, arduino toca melodia (FIM)
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_confirmar_coleta (
    p_item_id          IN  NUMBER,
    p_operador_id      IN  NUMBER,
    p_codigo_informado IN  VARCHAR2,
    p_qtd_coletada     IN  NUMBER,
    p_resultado        OUT VARCHAR2,   -- OK | ERRO_CODIGO | ERRO_SISTEMA
    p_mensagem         OUT VARCHAR2,
    p_comando_arduino  OUT VARCHAR2,   -- OK | ERRO | FIM
    p_tentativa        OUT NUMBER
) AS
    v_codigo_correto VARCHAR2(10);
    v_ordem_id       NUMBER;
    v_pendentes      NUMBER;
    v_tentativa      NUMBER;
BEGIN
    -- Busca código correto e a ordem do item
    SELECT e.codigo_verificacao, i.ordem_id
    INTO   v_codigo_correto, v_ordem_id
    FROM   itens_ordem i
    JOIN   enderecos   e ON e.id = i.endereco_id
    WHERE  i.id = p_item_id
      AND  i.status = 'PENDENTE';

    -- Número da tentativa atual para este item+operador
    SELECT NVL(MAX(tentativa), 0) + 1
    INTO   v_tentativa
    FROM   log_coleta
    WHERE  item_id = p_item_id AND operador_id = p_operador_id;

    p_tentativa := v_tentativa;

    -- Registra SEMPRE (rastreabilidade completa, inclusive erros)
    INSERT INTO log_coleta (item_id, operador_id, codigo_informado, sucesso, tentativa)
    VALUES (
        p_item_id,
        p_operador_id,
        UPPER(TRIM(p_codigo_informado)),
        CASE WHEN UPPER(TRIM(p_codigo_informado)) = UPPER(TRIM(v_codigo_correto))
             THEN 'S' ELSE 'N' END,
        v_tentativa
    );

    -- Valida o código
    IF UPPER(TRIM(p_codigo_informado)) != UPPER(TRIM(v_codigo_correto)) THEN
        COMMIT;  -- salva o log mesmo no erro
        p_resultado       := 'ERRO_CODIGO';
        p_mensagem        := 'Código incorreto. Tente novamente.';
        p_comando_arduino := 'ERRO';
        RETURN;
    END IF;

    -- Código correto: marca item como coletado
    UPDATE itens_ordem
    SET status       = 'COLETADO',
        qtd_coletada = p_qtd_coletada
    WHERE id = p_item_id;

    -- Verifica se restam itens pendentes na ordem
    SELECT COUNT(*) INTO v_pendentes
    FROM itens_ordem
    WHERE ordem_id = v_ordem_id AND status = 'PENDENTE';

    IF v_pendentes = 0 THEN
        -- Último item: conclui a ordem
        UPDATE ordens
        SET status       = 'CONCLUIDA',
            dt_conclusao = SYSDATE
        WHERE id = v_ordem_id;

        COMMIT;
        p_resultado       := 'OK';
        p_mensagem        := 'Ordem concluída! Parabéns.';
        p_comando_arduino := 'FIM';
    ELSE
        COMMIT;
        p_resultado       := 'OK';
        p_mensagem        := 'Item coletado. ' || v_pendentes || ' restante(s).';
        p_comando_arduino := 'OK';
    END IF;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_resultado       := 'ERRO_SISTEMA';
        p_mensagem        := 'Item não encontrado ou já coletado.';
        p_comando_arduino := 'ERRO';
    WHEN OTHERS THEN
        ROLLBACK;
        p_resultado       := 'ERRO_SISTEMA';
        p_mensagem        := SQLERRM;
        p_comando_arduino := 'ERRO';
END sp_confirmar_coleta;
/


-- ------------------------------------------------------------
-- SP_PAUSAR_ORDEM
-- Pausa uma ordem em andamento para retomada posterior.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_pausar_ordem (
    p_ordem_id  IN  NUMBER,
    p_resultado OUT VARCHAR2,
    p_mensagem  OUT VARCHAR2
) AS
BEGIN
    UPDATE ordens
    SET status = 'PAUSADA'
    WHERE id = p_ordem_id AND status = 'EM_ANDAMENTO';

    IF SQL%ROWCOUNT = 0 THEN
        p_resultado := 'ERRO';
        p_mensagem  := 'Ordem não encontrada ou não está em andamento.';
    ELSE
        COMMIT;
        p_resultado := 'OK';
        p_mensagem  := 'Ordem pausada.';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_resultado := 'ERRO';
        p_mensagem  := SQLERRM;
END sp_pausar_ordem;
/

COMMIT;
