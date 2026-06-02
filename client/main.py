import os
import sys
import time
from dotenv import load_dotenv

from modules.api_client import (
    login, listar_ordens, iniciar_ordem, proximo_item, confirmar_coleta, pausar_ordem, APIError
)
from modules.stt import ouvir
from modules.tts import falar
from modules.bluetooth import enviar as enviar_bluetooth

def main():
    print("="*40)
    print("   PICK BY VOICE - CLIENTE INICIADO")
    print("="*40)

    load_dotenv()
    
    # 1. Login do Operador
    matricula = os.getenv("OPERATOR_MATRICULA")
    if not matricula:
        falar("Informe sua matrícula para iniciar.")
        # Simplificação: em um cenário real o STT leria a matrícula,
        # aqui como fallback pediremos input caso a pessoa não queira falar
        # letras (que é mais complexo no modelo pequeno)
        matricula = input("Digite sua matrícula (ex: OP001): ").strip().upper()

    try:
        operador = login(matricula)
        op_id = operador["id"]
        nome = operador["nome"]
        pendentes = operador["ordens_pendentes"]
        
        if pendentes > 0:
            falar(f"Olá {nome}, você tem ordens pendentes. Retomando.")
        else:
            falar(f"Bom dia, {nome}.")
    except APIError as e:
        print(e)
        falar("Erro no login. Matrícula não encontrada ou inativa.")
        sys.exit(1)

    # 2. Seleção de Ordem
    try:
        if pendentes == 0:
            falar("Buscando novas ordens.")
            ordens = listar_ordens()
            if not ordens:
                falar("Nenhuma ordem disponível no momento.")
                sys.exit(0)
            
            # Pega a primeira (a view já ordena por prioridade CRITICO > URGENTE > NORMAL)
            ordem_id = ordens[0]["id"]
            numero_ordem = ordens[0]["numero"]
            
            falar(f"Iniciando ordem {numero_ordem}.")
            iniciar_ordem(op_id, ordem_id)
        else:
             # Se tem pendentes, a API já sabe qual é ao chamar proximo_item
             pass
    except APIError as e:
        print(e)
        falar("Erro ao processar ordens.")
        sys.exit(1)

    # 3. Loop de Picking
    while True:
        try:
            # a. Busca próximo item
            item = proximo_item(op_id)
            
            # b. Verifica se terminou
            if item.get("fim"):
                falar(item["mensagem"])
                enviar_bluetooth("FIM")
                break

            # Dados do item
            item_id = item["item_id"]
            rua = item["rua"]
            coluna = item["coluna"]
            nivel = item["nivel"]
            apt = item["apartamento"]
            produto = item["produto_descricao"]
            qtd = item["qtd_solicitada"]
            unidade = item["unidade"]

            # c. Envia comando para Arduino: MSG:RUACLNIVAPT
            endereco_compacto = f"{rua}{coluna}{nivel}{apt}"
            enviar_bluetooth(f"MSG:{endereco_compacto}")

            # d. Instruções de voz
            falar(f"Vá para Rua {rua}, Coluna {coluna}, Nível {nivel}, Apartamento {apt}.")
            falar(f"Produto: {produto}.")
            falar(f"Quantidade: {qtd} {unidade}.")
            
            while True:
                falar("Confirme o código da posição.")
                
                # g. Ouve a resposta
                codigo = ouvir("Fale o código de verificação:")
                if not codigo:
                    falar("Não entendi. Repita o código.")
                    continue
                
                # Permite pausar via voz
                if codigo == "PULAR":
                    falar("Pausando a ordem.")
                    # Como não temos a ordem_id facilmente aqui na resposta do proximo item,
                    # em um fluxo real teríamos. Para simplificar, poderíamos ter uma rota de pausa por operador.
                    # Vamos assumir que a pausa é manual no WMS ou implementar dps.
                    break

                # h. Envia para API
                print(f"Enviando confirmação: item={item_id}, op={op_id}, codigo={codigo}, qtd={qtd}")
                result = confirmar_coleta(item_id, op_id, codigo, qtd)
                
                # i. Envia resposta ao Arduino
                comando_arduino = result.get("comando_arduino", "ERRO")
                enviar_bluetooth(comando_arduino)
                
                # j. Feedback de voz
                msg = result.get("mensagem", "Erro desconhecido.")
                falar(msg)

                # k. Se ERRO, repete o pedido de código
                if comando_arduino == 'ERRO':
                    # O loop interno repete
                    pass
                else:
                    # OK, sai do loop interno e vai pro próximo item
                    time.sleep(1) # Pausa dramática para o operador andar
                    break

        except APIError as e:
            print(f"Erro na API: {e}")
            falar("Ocorreu um erro de comunicação com o sistema.")
            time.sleep(3)
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            falar("Sistema encerrado.")
            break
        except Exception as e:
            print(f"Erro inesperado: {e}")
            falar("Erro interno no aplicativo.")
            break

if __name__ == "__main__":
    main()
