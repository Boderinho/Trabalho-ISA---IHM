import random
import math

# #esboço parte da esteira 
# #Ligar e desligar a esteira.

# Sortear as quatro faixas de operação.
# Sortear a velocidade a cada 10 segundos.
# Determinar o intervalo de entrada de peças
# Informar ao simulador os instantes das próximas mudanças.


class Esteira:

    TEMPO_MUDANCA_FAIXA = 30.0
    TEMPO_MUDANCA_VELOCIDADE = 10.0

    # Faixas de velocidade
    LIMITES_FAIXAS = {

        1: (1.00, 1.25),

        2: (1.25, 1.50),

        3: (1.50, 1.75),

        4: (1.75, 2.00)

    }


    # Intervalo em segundos para entrada de peças novas
    INTERVALOS_PECAS = {

        1: 12.0,

        2: 10.0,

        3: 8.0,

        4: 6.0

    }

    def atualizar(self, planta, delta_t):

        if delta_t <= 0:
            return

        # Se estiver desligada, os temporizadores ficam pausados.
        if not planta.esteira_ligada:

            planta.velocidade = 0.0

            return

        tempo_restante = float(delta_t)

        tolerancia = 1e-9

        while True:

            # Primeiro, verifica a mudança de faixa.
            if planta.proxima_mudanca_faixa <= tolerancia:

                self.sortear_faixa(planta)

                planta.proxima_mudanca_faixa = self.TEMPO_MUDANCA_FAIXA

            # Depois, verifica a mudança de velocidade.
            if planta.proxima_mudanca_velocidade <= tolerancia:

                self.sortear_velocidade(planta)

                planta.proxima_mudanca_velocidade = self.TEMPO_MUDANCA_VELOCIDADE

            if tempo_restante <= tolerancia:
                break


            #Contagem dos Temporizadores
            proximo_evento = min(planta.proxima_mudanca_faixa,planta.proxima_mudanca_velocidade)

            intervalo = min(tempo_restante,proximo_evento)

            planta.proxima_mudanca_faixa -= intervalo

            planta.proxima_mudanca_velocidade -= intervalo

            tempo_restante = max(0.0,tempo_restante - intervalo)

        

    def desligar_por_temperatura(self, planta, temperatura):

        if temperatura >= 100:

            planta.esteira_ligada = False

            planta.velocidade = 0

            return True
        

        return False


    def sortear_faixa(self, planta):
        
        planta.faixa = random.randint(1,4)

    
    def sortear_velocidade(self, planta):
        
        limite_inferior, limite_superior = (self.LIMITES_FAIXAS[planta.faixa])

        if planta.faixa > 1:

            limite_inferior = math.nextafter(limite_inferior, math.inf)

        planta.velocidade = random.uniform(limite_inferior, limite_superior)

                    
    def intervalo_pecas(self, planta):
        return self.INTERVALOS_PECAS(planta.faixa)

