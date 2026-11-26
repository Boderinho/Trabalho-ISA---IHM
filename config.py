"""Configuração compartilhada entre o servidor Modbus e a API.

Mapa de registradores (endereços 0-based, como na pyModbusTCP):

    Coil 0             Estado da esteira (0 = desligada, 1 = ligada)  leitura e escrita
    Holding 0-1        Velocidade da esteira, REAL (float32, m/s)     só leitura
    Holding 2-3        Temperatura do motor, REAL (float32, °C)       só leitura
    Holding 4          Produção total, INT (16 bits sem sinal)        só leitura
    Holding 5          Peças aprovadas, INT (16 bits sem sinal)       só leitura
    Holding 6          Peças rejeitadas, INT (16 bits sem sinal)      só leitura

Os REAIS usam a mesma codificação da prática (encode_ieee + long_list_to_word):
IEEE 754 de 32 bits, 2 registradores, palavra mais significativa primeiro.

Os INT ocupam 1 registrador (0 a 65.535). Por isso CONTADOR_MAX em planta.py
deve ser 65_535.
"""

# Rede
MODBUS_HOST = "localhost"
MODBUS_PORTA = 5020          # 502 exige privilégio de administrador

# Coils
COIL_ESTEIRA = 0

# Holding registers
REG_VELOCIDADE = 0           # 2 registradores
REG_TEMPERATURA = 2          # 2 registradores
REG_TOTAL = 4
REG_APROVADAS = 5
REG_REJEITADAS = 6

# Bloco lido de uma só vez (uma leitura do bloco = um passo da simulação)
REG_INICIO = 0
QTD_REGS = 7