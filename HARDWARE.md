# Guia de Montagem de Hardware - Pick By Voice

Para que o projeto seja avaliado e reproduzido corretamente na cadeira de Microcontroladores, siga as instruções de montagem do circuito eletrônico abaixo.

## 🛠️ Lista de Materiais (BOM - Bill of Materials)

*   1x **Arduino Uno** (ou Nano/Mega)
*   1x **Módulo Bluetooth HC-05** ou HC-06
*   1x **Display LCD 16x2 com Módulo I2C**
*   1x **Buzzer Ativo** 5V
*   3x **LEDs** (1x Verde, 1x Vermelho, 1x Amarelo/Azul)
*   3x **Resistores de 220Ω a 330Ω** (Para os LEDs)
*   1x **Protoboard**
*   **Jumpers** (Macho-Macho e Macho-Fêmea)

---

## 🔌 Esquema de Ligações (Pinagem)

### 1. LEDs e Buzzer
*   **LED Verde (Sucesso / OK)**
    *   Anodo (perna maior) -> Resistor -> Pino Digital **8**
    *   Catodo (perna menor) -> GND
*   **LED Vermelho (Erro)**
    *   Anodo -> Resistor -> Pino Digital **9**
    *   Catodo -> GND
*   **LED Amarelo/Azul (Alerta de Endereço / Tarefa)**
    *   Anodo -> Resistor -> Pino Digital **13**
    *   Catodo -> GND
*   **Buzzer**
    *   Pino Positivo (+) -> Pino Digital **10**
    *   Pino Negativo (-) -> GND

### 2. Display LCD I2C
*   **GND** -> GND do Arduino
*   **VCC** -> 5V do Arduino
*   **SDA** -> Pino **A4** do Arduino Uno (ou pino SDA específico)
*   **SCL** -> Pino **A5** do Arduino Uno (ou pino SCL específico)

### 3. Módulo Bluetooth HC-05
*   **VCC** -> 5V do Arduino
*   **GND** -> GND do Arduino
*   **TXD** -> Pino **RX (0)** do Arduino
*   **RXD** -> Pino **TX (1)** do Arduino (Recomendado usar divisor de tensão 5V -> 3.3V no pino RX do HC-05 para maior durabilidade)

> **⚠️ IMPORTANTE SOBRE O BLUETOOTH:** 
> Como o módulo Bluetooth está utilizando as portas de Hardware Serial nativas do Arduino (Pinos 0 e 1), você **DEVE DESCONECTAR** os pinos TX e RX do Bluetooth sempre que for enviar um novo código (fazer o upload do sketch `.ino`) para o Arduino pelo computador. Após o upload, reconecte-os para o uso do sistema.

---

## 📡 Funcionamento do Hardware

1.  **Aguardando Tarefa:** O LCD exibe "PICK BY VOICE" e "Aguardando...".
2.  **Recebimento de Tarefa:** O app envia o comando via Bluetooth (`MSG:A0111`). O Arduino apita (`Buzzer`), acende o **LED de Alerta (Pino 13)** e mostra no LCD o endereço "A0111".
3.  **Confirmação Correta:** Se o operador acertar o código, o app manda `OK`. O Arduino apaga o LED de Alerta, acende o **LED Verde (Pino 8)** e emite um bipe curto de sucesso.
4.  **Confirmação Incorreta:** Se o operador errar o código, o app manda `ERRO`. O Arduino acende o **LED Vermelho (Pino 9)** e emite um bipe longo de erro, limpando a parte debaixo do LCD para nova tentativa.
5.  **Fim do Expediente:** Quando acabam os itens da ordem, o app manda `FIM`. Todos os LEDs piscam e o LCD avisa para ir para a expedição.
