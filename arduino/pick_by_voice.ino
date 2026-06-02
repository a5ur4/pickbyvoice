/**
 * Pick By Voice - Arduino Firmware
 * 
 * Este sketch controla a interface física (LEDs, LCD, Buzzer) do sistema
 * de separação por voz. Ele recebe comandos via Bluetooth (Serial) vindos
 * do cliente Python e fornece feedback visual/sonoro para o operador.
 * 
 * Protocolo de Comandos:
 * - "MSG:RUACLNIVAPT" -> Exibe o endereço no LCD e acende LED de alerta.
 * - "OK"              -> Feedback de sucesso (LED Verde + Bipe curto).
 * - "ERRO"            -> Feedback de erro (LED Vermelho + Bipe longo).
 * - "FIM"             -> Finaliza a coleta (Pisca todos os LEDs).
 */

#include <LiquidCrystal_I2C.h> // Biblioteca para LCD I2C

// --- Configurações de Hardware ---
const int PIN_LED_OK    = 8;
const int PIN_LED_ERRO  = 9;
const int PIN_BUZZER    = 10;
const int PIN_LED_ALERTA = 13;

// Inicializa o LCD (Endereço 0x27, 16 colunas, 2 linhas)
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  // Inicializa comunicação Serial (Bluetooth HC-05 costuma usar 9600 baud)
  Serial.begin(9600);
  
  // Configura pinos
  pinMode(PIN_LED_OK, OUTPUT);
  pinMode(PIN_LED_ERRO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_ALERTA, OUTPUT);

  // Inicializa LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("PICK BY VOICE");
  lcd.setCursor(0, 1);
  lcd.print("Aguardando...");

  // Bipes de inicialização
  beep(100);
  delay(100);
  beep(100);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("MSG:")) {
      handleMessage(command.substring(4));
    } else if (command == "OK") {
      handleOk();
    } else if (command == "ERRO") {
      handleErro();
    } else if (command == "FIM") {
      handleFim();
    }
  }
}

// --- Handlers de Comandos ---

void handleMessage(String address) {
  // Exemplo: MSG:A0111 -> Rua A, Col 01, Niv 1, Apt 1
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Vá para:");
  lcd.setCursor(0, 1);
  lcd.print(address);
  
  digitalWrite(PIN_LED_ALERTA, HIGH);
  beep(200);
}

void handleOk() {
  digitalWrite(PIN_LED_ALERTA, LOW);
  digitalWrite(PIN_LED_OK, HIGH);
  lcd.setCursor(13, 0);
  lcd.print("OK ");
  beep(100);
  delay(500);
  digitalWrite(PIN_LED_OK, LOW);
}

void handleErro() {
  digitalWrite(PIN_LED_ERRO, HIGH);
  lcd.setCursor(12, 0);
  lcd.print("ERRO");
  beep(600);
  delay(500);
  digitalWrite(PIN_LED_ERRO, LOW);
  lcd.setCursor(12, 0);
  lcd.print("    ");
}

void handleFim() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("COLETA FINALIZ.");
  lcd.setCursor(0, 1);
  lcd.print("Vá p/ expedição");
  
  for(int i=0; i<5; i++) {
    digitalWrite(PIN_LED_OK, HIGH);
    digitalWrite(PIN_LED_ERRO, HIGH);
    beep(100);
    delay(100);
    digitalWrite(PIN_LED_OK, LOW);
    digitalWrite(PIN_LED_ERRO, LOW);
    delay(100);
  }
}

void beep(int duration) {
  digitalWrite(PIN_BUZZER, HIGH);
  delay(duration);
  digitalWrite(PIN_BUZZER, LOW);
}
