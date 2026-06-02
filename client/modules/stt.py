import os
import json
import queue
import logging
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv
from word2number import w2n

load_dotenv()

MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "./model")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    model = Model(MODEL_PATH)
    logging.info("Modelo Vosk carregado com sucesso.")
except Exception as e:
    logging.error(f"Erro ao carregar o modelo Vosk. Certifique-se de que a pasta 'model' existe em {MODEL_PATH}. Erro: {e}")
    model = None

# Dicionário simples para conversão de números por extenso em PT-BR para dígitos
# pois word2number é focado em inglês, para pt-br precisamos de um parse simples
num_ptbr = {
    "zero": "0", "um": "1", "uma": "1", "dois": "2", "duas": "2", "três": "3", "tres": "3", "quatro": "4", "cinco": "5",
    "seis": "6", "meia": "6", "sete": "7", "oito": "8", "nove": "9", "dez": "10", "onze": "11", "doze": "12",
    "treze": "13", "quatorze": "14", "catorze": "14", "quinze": "15", "dezesseis": "16", "dezasseis": "16",
    "dezessete": "17", "dezoito": "18", "dezenove": "19", "vinte": "20", "trinta": "30", "quarenta": "40",
    "cinquenta": "50", "sessenta": "60", "setenta": "70", "oitenta": "80", "noventa": "90"
}

def convert_to_digits(text: str) -> str:
    """Converte números por extenso em PT-BR para dígitos, simplificado."""
    words = text.split()
    digits = ""
    for word in words:
        if word in num_ptbr:
            digits += num_ptbr[word]
        elif word.isdigit():
            digits += word
    return digits if digits else text

def ouvir(prompt: str = "Aguardando comando...") -> str:
    """Ouve o microfone e retorna o texto reconhecido."""
    if not model:
        # Modo simulado caso o modelo não exista
        return input(f"{prompt} (Simulação STT, digite o código): ").strip().upper()

    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    try:
        # Restringe o vocabulário para melhorar a precisão
        vocab = '["zero", "um", "uma", "dois", "duas", "três", "tres", "quatro", "cinco", "seis", "meia", "sete", "oito", "nove", "dez", "onze", "doze", "treze", "quatorze", "catorze", "quinze", "dezesseis", "dezasseis", "dezessete", "dezoito", "dezenove", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa", "e", "ok", "confirmar", "feito", "pular"]'
        rec = KaldiRecognizer(model, 16000, vocab)
        
        print(f"\n[Microfone Aberto] {prompt}")
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get("text", "")
                    if text:
                        text_digits = convert_to_digits(text)
                        print(f"-> Reconhecido: {text} | Convertido: {text_digits}")
                        return text_digits.strip().upper()
                else:
                    pass # partial results can be checked with rec.PartialResult()
    except Exception as e:
        logging.error(f"Erro no STT: {e}")
        return ""
