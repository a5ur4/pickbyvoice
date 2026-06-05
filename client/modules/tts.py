import sys

try:
    import pyttsx3
    engine = pyttsx3.init()

    # Tenta configurar voz em português, caso disponível
    voices = engine.getProperty('voices')
    for voice in voices:
        if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 150) # Velocidade da fala
    engine.setProperty('volume', 1.0) # Volume máximo
except Exception as e:
    print(f"[AVISO] Motor TTS não inicializado (falta dependência de áudio no SO): {e}")
    engine = None

def falar(texto: str) -> None:
    print(f"[VOZ]: {texto}")
    if engine:
        try:
            engine.say(texto)
            engine.runAndWait()
        except:
            pass
