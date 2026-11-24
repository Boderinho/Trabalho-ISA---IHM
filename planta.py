
import time

from threading import RLock
from esteira import *

class PlantaIndustrial:

    def __init__(self):

        # ==================================================
        # CONTROLE TEMPORAL
        # ==================================================

        # Relógio monotônico: evita problemas com ajustes
        # no relógio do sistema operacional.
        self.ultimo_processamento = time.monotonic()

        # Tempo acumulado da simulação, em segundos.
        self.tempo_simulacao = 0.0

        # Proteção contra atualizações simultâneas.
        self.lock = RLock()

        # ==================================================
        # ESTADO INICIAL DA PLANTA
        # ==================================================

        self.esteira_ligada = True
        self.velocidade = 2.0
        self.faixa = 4 #coloquei isso aqui para conseguir me localizar em qual faixa que eu estou e com base nisso fazer os sorteios de velocidade
        self.temperatura = 30.0

        # Contadores de produção.
        self.producao_total = 0
        self.pecas_aprovadas = 0
        self.pecas_rejeitadas = 0

        # Sensores.
        self.sensor_entrada = False
        self.sensor_saida = False

        # Resultado da última inspeção.
        # None = nenhuma inspeção realizada.
        # True = aprovada.
        # False = reprovada.
        self.resultado_inspecao = None

        # ==================================================
        # ESTADO INTERNO DA SIMULAÇÃO
        # ==================================================

        # Lista de peças presentes na esteira.
        self.pecas = []

        # Lista de alarmes ativos.
        self.alarmes = []

        # Histórico de eventos ocorridos.
        self.historico_eventos = []

        # ==================================================
        # PRÓXIMOS EVENTOS
        # ==================================================

        self.proxima_mudanca_faixa = 30.0
        self.proxima_mudanca_velocidade = 10.0
        self.proxima_entrada_peca = None

        # ==================================================
        # INICIALIZAÇÃO DOS MÓDULOS
        # ==================================================

        # Os módulos serão adicionados conforme forem
        # desenvolvidos:
        #
        # self.esteira = Esteira()
        # self.pecas = GerenciadorPecas()
        # self.inspecao = Inspecao()
        # self.temperatura_motor = Temperatura()
        # self.alarmes = GerenciadorAlarmes()

    # ======================================================
    # ATUALIZAÇÃO PRINCIPAL
    # ======================================================

    def atualizar(self):

        """
        Atualiza o estado da planta com base no tempo
        transcorrido desde o último processamento.

        Este método será chamado quando houver uma
        solicitação de leitura ao servidor Modbus.
        """

        with self.lock:

            agora = time.monotonic()

            delta_t = agora - self.ultimo_processamento

            if delta_t <= 0:
                return self.obter_variaveis()

            # Atualiza o tempo de referência.
            self.ultimo_processamento = agora

            # Avança o relógio interno da simulação.
            self.tempo_simulacao += delta_t

            # Processa os eventos ocorridos no intervalo.
            self.processar_eventos(delta_t)

            # Verifica a consistência da planta.
            self.verificar_consistencia()

            # Retorna as variáveis atualizadas.
            return self.obter_variaveis()

    # ======================================================
    # PROCESSAMENTO DOS EVENTOS
    # ======================================================

    def processar_eventos(self, delta_t):

        """
        Coordena o processamento dos eventos da planta.

        IMPORTANTE:
        Esta estrutura ainda não implementa a cronologia
        dos eventos. Ela será desenvolvida posteriormente.
        """

        # 1. Atualizar sorteios de velocidade e faixa.
        # self.esteira.atualizar(delta_t)

        # 2. Gerar novas peças.
        # self.gerenciador_pecas.atualizar_entradas(delta_t)

        # 3. Atualizar posição das peças.
        # self.gerenciador_pecas.atualizar_movimentacao(delta_t)

        # 4. Verificar entrada, inspeção e saída.
        # self.inspecao.atualizar(delta_t)

        # 5. Atualizar temperatura do motor.
        # self.temperatura_motor.atualizar(delta_t)

        # 6. Verificar alarmes.
        # self.gerenciador_alarmes.atualizar(delta_t)

        pass

    # ======================================================
    # VERIFICAÇÃO DE CONSISTÊNCIA
    # ======================================================

    def verificar_consistencia(self):

        # A velocidade deve ser zero quando a esteira
        # estiver desligada.
        if not self.esteira_ligada:
            self.velocidade = 0.0

        # A produção total deve corresponder à soma
        # das peças aprovadas e rejeitadas.
        if self.producao_total != (
            self.pecas_aprovadas + self.pecas_rejeitadas
        ):
            raise RuntimeError(
                "Inconsistência nos contadores de produção."
            )

        # Limites da temperatura.
        self.temperatura = max(
            25.0,
            min(110.0, self.temperatura)
        )

        # Limites físicos da velocidade.
        self.velocidade = max(
            0.0,
            min(2.0, self.velocidade)
        )

    # ======================================================
    # DISPONIBILIZAÇÃO DAS VARIÁVEIS
    # ======================================================

    def obter_variaveis(self):

        """
        Retorna as nove variáveis principais da planta.

        Este dicionário será utilizado posteriormente
        para alimentar os registradores Modbus.
        """

        with self.lock:

            return {

                "velocidade": float(self.velocidade),

                "temperatura": float(self.temperatura),

                "producao_total": int(self.producao_total),

                "pecas_aprovadas": int(self.pecas_aprovadas),

                "pecas_rejeitadas": int(self.pecas_rejeitadas),

                "esteira_ligada": bool(self.esteira_ligada),

                "sensor_entrada": bool(self.sensor_entrada),

                "sensor_saida": bool(self.sensor_saida),

                "resultado_inspecao": self.resultado_inspecao

            }


# ==========================================================
# TESTE INICIAL DO SIMULADOR
# ==========================================================

if __name__ == "__main__":

    planta = PlantaIndustrial()

    print("Simulador industrial inicializado.")

    while True:

        # Simula uma solicitação de leitura.
        variaveis = planta.atualizar()

        print("\nTempo de simulação:",
              round(planta.tempo_simulacao, 2), "s")

        print("Variáveis da planta:")
        print(variaveis)

        # Intervalo apenas para simular requisições.
        # Não representa um ciclo interno da planta.
        time.sleep(2)
