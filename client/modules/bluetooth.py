import os
import serial
import time
import logging
from dotenv import load_dotenv

load_dotenv()

BT_PORT = os.getenv("BT_PORT")
ser = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def conectar():
    global ser
    if not BT_PORT:
        logging.warning("Nenhuma porta Bluetooth/Serial configurada. Executando em modo de simulação.")
        return

    try:
        ser = serial.Serial(BT_PORT, 9600, timeout=1)
        time.sleep(2)  # Aguarda conexão estabilizar
        logging.info(f"Conectado à porta {BT_PORT}")
    except serial.SerialException as e:
        logging.error(f"Erro ao conectar na porta {BT_PORT}: {e}")
        ser = None

def enviar(comando: str) -> None:
    global ser
    
    if not BT_PORT or not ser:
        print(f"[ARDUINO SIMULADO] Comando recebido: {comando}")
        return

    try:
        comando_formatado = f"{comando}\n"
        ser.write(comando_formatado.encode('utf-8'))
        ser.flush()
        logging.info(f"Comando enviado ao Arduino: {comando}")
    except serial.SerialException as e:
        logging.error(f"Falha ao enviar comando via Bluetooth: {e}")
        # Tentar reconectar
        logging.info("Tentando reconectar...")
        conectar()
        if ser:
            try:
                ser.write(comando_formatado.encode('utf-8'))
                ser.flush()
            except:
                logging.error("Falha ao enviar comando após reconexão.")

conectar()
