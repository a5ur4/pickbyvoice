/**
 * Pick By Voice - MODO DEMONSTRAÇÃO (STANDALONE)
 * 
 * Este sketch simula o sistema completo sem precisar do backend em Python/Oracle.
 * Ideal para feiras de ciências e apresentações onde não há servidor disponível.
 * 
 * Como usar na apresentação:
 * 1. O Arduino mostrará a posição (Ex: A0111) no LCD e acenderá o LED Amarelo.
 * 2. Abra o "Monitor Serial" na IDE do Arduino (9600 baud, "Ambos em NL & CR").
 * 3. Digite o código correto (Ex: 11) e dê Enter para simular o acerto.
 * 4. Digite um código errado para mostrar o sistema de erro.
 * 5. Se não digitar nada por 8 segundos, ele avança sozinho (piloto automático).
 */

#include <LiquidCrystal_I2C.h>

// --- Configurações de Hardware ---
const int PIN_LED_OK     = 8;
const int PIN_LED_ERRO   = 9;
const int PIN_BUZZER     = 10;
const int PIN_LED_ALERTA = 13;

LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- Dados Simulados (O que viria da API) ---
struct Tarefa {
  String endereco;
  String codigo_correto;
};

Tarefa tarefas[] = {
  {"A0111", "11"},
  {"A0112", "47"},
  {"B0321", "99"}
};

int total_tarefas = 3;
int tarefa_atual = 0;
bool ordem_finalizada = false;

// Controle de tempo para o Piloto Automático
unsigned long tempo_inicio_tarefa = 0;
const unsigned long TEMPO_ESPERA = 8000; // 8 segundos

void setup() {
  Serial.begin(9600);
  
  pinMode(PIN_LED_OK, OUTPUT);
  pinMode(PIN_LED_ERRO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_ALERTA, OUTPUT);

  lcd.init();
  lcd.backlight();
  
  lcd.setCursor(0, 0);
  lcd.print("PICK BY VOICE");
  lcd.setCursor(0, 1);
  lcd.print("Modo Demo Inic.");
  
  beep(100); delay(100); beep(100);
  delay(2000);
  
  mostrarTarefa();
}

void loop() {
  if (ordem_finalizada) return;

  // Verifica se o usuário digitou algo no Monitor Serial
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    if (input.length() > 0) {
      Serial.print("Codigo recebido: ");
      Serial.println(input);
      validarCodigo(input);
    }
  }

  // Verifica se o tempo estourou (Piloto Automático)
  if (millis() - tempo_inicio_tarefa > TEMPO_ESPERA) {
    Serial.println("Tempo esgotado. Avancando no Piloto Automatico...");
    validarCodigo(tarefas[tarefa_atual].codigo_correto); // Simula acerto
  }
}

// --- Funções de Lógica ---

void mostrarTarefa() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Va para:");
  lcd.setCursor(0, 1);
  lcd.print(tarefas[tarefa_atual].endereco);
  
  digitalWrite(PIN_LED_ALERTA, HIGH);
  beep(200);
  
  tempo_inicio_tarefa = millis(); // Reseta o cronômetro
  
  Serial.println("---------------------------------");
  Serial.print("Nova Tarefa: ");
  Serial.println(tarefas[tarefa_atual].endereco);
  Serial.print("Digite o codigo (Esperado: ");
  Serial.print(tarefas[tarefa_atual].codigo_correto);
  Serial.println("):");
}

void validarCodigo(String codigo_informado) {
  if (codigo_informado == tarefas[tarefa_atual].codigo_correto) {
    // ACERTOU
    digitalWrite(PIN_LED_ALERTA, LOW);
    digitalWrite(PIN_LED_OK, HIGH);
    lcd.setCursor(13, 0);
    lcd.print("OK ");
    beep(100);
    delay(1000);
    digitalWrite(PIN_LED_OK, LOW);
    
    tarefa_atual++;
    
    if (tarefa_atual >= total_tarefas) {
      finalizarOrdem();
    } else {
      mostrarTarefa();
    }
  } else {
    // ERROU
    digitalWrite(PIN_LED_ERRO, HIGH);
    lcd.setCursor(11, 0);
    lcd.print(" ERRO");
    beep(600);
    delay(1000);
    digitalWrite(PIN_LED_ERRO, LOW);
    lcd.setCursor(11, 0);
    lcd.print("     ");
    
    tempo_inicio_tarefa = millis(); // Dá mais 8 segundos para tentar de novo
    Serial.println("Codigo incorreto. Tente novamente.");
  }
}

void finalizarOrdem() {
  ordem_finalizada = true;
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("COLETA FINALIZ.");
  lcd.setCursor(0, 1);
  lcd.print("Va p/ expedicao");
  
  Serial.println("Ordem finalizada com sucesso!");
  
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
