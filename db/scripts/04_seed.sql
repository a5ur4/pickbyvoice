-- ============================================================
-- Script 04 — Dados de Teste
-- Roda no schema do APP_USER (pickvoice) automaticamente.
-- ============================================================

-- Setores
INSERT INTO setores (codigo, descricao) VALUES ('SEC', 'Seco');
INSERT INTO setores (codigo, descricao) VALUES ('REF', 'Refrigerado');
INSERT INTO setores (codigo, descricao) VALUES ('FRA', 'Frágil');
INSERT INTO setores (codigo, descricao) VALUES ('PES', 'Pesado');

-- Operadores
INSERT INTO operadores (nome, matricula) VALUES ('João Silva',   'OP001');
INSERT INTO operadores (nome, matricula) VALUES ('Maria Santos', 'OP002');
INSERT INTO operadores (nome, matricula) VALUES ('Carlos Lima',  'OP003');

-- Produtos
INSERT INTO produtos (codigo, descricao, unidade, categoria) VALUES ('ARR001', 'Arroz Branco 5kg',     'CX', 'Seco');
INSERT INTO produtos (codigo, descricao, unidade, categoria) VALUES ('FEI001', 'Feijão Carioca 1kg',   'CX', 'Seco');
INSERT INTO produtos (codigo, descricao, unidade, categoria) VALUES ('OLE001', 'Óleo de Soja 900ml',   'UN', 'Seco');
INSERT INTO produtos (codigo, descricao, unidade, categoria) VALUES ('LEI001', 'Leite Integral 1L',    'UN', 'Refrigerado');
INSERT INTO produtos (codigo, descricao, unidade, categoria) VALUES ('MOL001', 'Molho de Tomate 340g', 'UN', 'Frágil');
INSERT INTO produtos (codigo, descricao, unidade, categoria) VALUES ('AGU001', 'Água Mineral 20L',     'UN', 'Pesado');

-- Endereços (rua, coluna, nivel, apartamento, codigo_verificacao, setor_id)
INSERT INTO enderecos (rua,coluna,nivel,apartamento,codigo_verificacao,setor_id) VALUES ('A','01','1','1','11',1);
INSERT INTO enderecos (rua,coluna,nivel,apartamento,codigo_verificacao,setor_id) VALUES ('A','01','1','2','12',1);
INSERT INTO enderecos (rua,coluna,nivel,apartamento,codigo_verificacao,setor_id) VALUES ('A','02','1','1','21',1);
INSERT INTO enderecos (rua,coluna,nivel,apartamento,codigo_verificacao,setor_id) VALUES ('B','01','1','1','47',1);
INSERT INTO enderecos (rua,coluna,nivel,apartamento,codigo_verificacao,setor_id) VALUES ('C','01','1','1','61',2);
INSERT INTO enderecos (rua,coluna,nivel,apartamento,codigo_verificacao,setor_id) VALUES ('D','01','1','1','81',3);
INSERT INTO enderecos (rua,coluna,nivel,apartamento,codigo_verificacao,setor_id) VALUES ('E','01','1','1','91',4);

-- Estoque (produto_id, endereco_id, quantidade)
INSERT INTO estoque (produto_id, endereco_id, quantidade) VALUES (1, 1, 50);
INSERT INTO estoque (produto_id, endereco_id, quantidade) VALUES (2, 2, 80);
INSERT INTO estoque (produto_id, endereco_id, quantidade) VALUES (3, 3, 30);
INSERT INTO estoque (produto_id, endereco_id, quantidade) VALUES (4, 5, 60);
INSERT INTO estoque (produto_id, endereco_id, quantidade) VALUES (5, 6, 40);
INSERT INTO estoque (produto_id, endereco_id, quantidade) VALUES (6, 7, 15);

-- Ordens
INSERT INTO ordens (numero, prioridade) VALUES ('ORD-001', 'NORMAL');
INSERT INTO ordens (numero, prioridade) VALUES ('ORD-002', 'URGENTE');

-- Itens Ordem 1 (sequência otimizada: Rua A → B → C → D)
INSERT INTO itens_ordem (ordem_id,produto_id,endereco_id,sequencia,qtd_solicitada) VALUES (1,1,1,1,3);
INSERT INTO itens_ordem (ordem_id,produto_id,endereco_id,sequencia,qtd_solicitada) VALUES (1,2,2,2,5);
INSERT INTO itens_ordem (ordem_id,produto_id,endereco_id,sequencia,qtd_solicitada) VALUES (1,4,5,3,10);
INSERT INTO itens_ordem (ordem_id,produto_id,endereco_id,sequencia,qtd_solicitada) VALUES (1,5,6,4,4);

-- Itens Ordem 2
INSERT INTO itens_ordem (ordem_id,produto_id,endereco_id,sequencia,qtd_solicitada) VALUES (2,3,3,1,2);
INSERT INTO itens_ordem (ordem_id,produto_id,endereco_id,sequencia,qtd_solicitada) VALUES (2,6,7,2,1);

COMMIT;
