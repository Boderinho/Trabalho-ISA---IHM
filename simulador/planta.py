"""Simulador da linha de esteira.

Cada chamada de tick() avança um passo de ~2 s de processo.
O servidor Modbus chama tick() a cada leitura, então a planta
só muda quando alguém consulta.

Este arquivo contempla apenas a geração de dados para a 
simulação do contexto. A regras de automação ficam no webservice (IHM streamlit)
e no scadaBR.
"""

import random

# Parâmetros do processo (ajustar na calibração)
TEMP_INICIAL = 30.0       # °C
TEMP_MIN = 25.0           # °C
TEMP_MAX = 110.0          # °C
AQUECIMENTO = 0.4         # °C por passo, por m/s de velocidade
RESFRIAMENTO = 0.5        # °C por passo com a esteira desligada
VEL_MIN = 1.0             # m/s
VEL_MAX = 2.0             # m/s
VEL_INI = 1.5             # m/s
VEL_DESVIO = 0.1
PROB_APROVACAO = 0.95
CONTADOR_MAX = 100_000


class Planta:

    def __init__(self, semente=None):
        # Gerador próprio: com semente fixa, os testes se repetem
        self.rng = random.Random(semente)

        self.esteira_ligada = True
        self.velocidade = VEL_INI
        self.temperatura = TEMP_INICIAL
        self.producao_total = 0
        self.pecas_aprovadas = 0
        self.pecas_rejeitadas = 0

    def definir_esteira(self, ligada):
        # Chamado quando o coil da esteira é escrito (via Modbus).
        ligada = bool(ligada)
        if ligada and not self.esteira_ligada:
            self.velocidade = VEL_INI

        if not ligada:
            self.velocidade = 0.0    

        self.esteira_ligada = ligada

    def tick(self):
        # Avança a planta em um passo.
        if self.esteira_ligada:
            v = self.velocidade + self.rng.gauss(0, VEL_DESVIO)
            self.velocidade = max(VEL_MIN, min(VEL_MAX, v))
            self.temperatura += AQUECIMENTO * self.velocidade
            self._produzir_peca()
        else:
            self.velocidade = 0.0
            self.temperatura -= RESFRIAMENTO

        self.temperatura = max(TEMP_MIN, min(TEMP_MAX, self.temperatura))

    def _produzir_peca(self):
        # A 2 m/s a probabilidade é 1/3 por passo (2 s): ~10 peças/min
        if self.producao_total >= CONTADOR_MAX:
            return
        if self.rng.random() < self.velocidade / 6:
            self.producao_total += 1
            if self.rng.random() < PROB_APROVACAO:
                self.pecas_aprovadas += 1
            else:
                self.pecas_rejeitadas += 1

    def obter_variaveis(self):
        """Valores em unidades reais. A conversão para registradores
        (velocidade x 100, temperatura x 10) fica na camada Modbus."""
        return {
            "esteira_ligada": self.esteira_ligada,
            "velocidade": self.velocidade,
            "temperatura": self.temperatura,
            "producao_total": self.producao_total,
            "pecas_aprovadas": self.pecas_aprovadas,
            "pecas_rejeitadas": self.pecas_rejeitadas,
        }


if __name__ == "__main__":
    import time

    planta = Planta()
    print("Teste do simulador (Ctrl+C para sair)")
    try:
        while True:
            planta.tick()
            v = planta.obter_variaveis()
            print(f"ligada={v['esteira_ligada']!s:5}  "
                  f"vel={v['velocidade']:.2f}  temp={v['temperatura']:.1f}  "
                  f"total={v['producao_total']}  "
                  f"aprov={v['pecas_aprovadas']}  rej={v['pecas_rejeitadas']}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulação Encerrando... .. .")