from planta import *
import random


# #esboço parte da esteira 
# #Ligar e desligar a esteira.

# Sortear as quatro faixas de operação.
# Sortear a velocidade a cada 10 segundos.
# Determinar o intervalo de entrada de peças
# Informar ao simulador os instantes das próximas mudanças.


class Esteira:

    def __init__(self):
        
        self.esteira_ligada = True

        def LigaDesliga(self, temperatura):

            if temperatura >= 100:
                self.esteira_ligada = False

                return self.esteira_ligada
        
            self.esteira_ligada = True

            return self.esteira_ligada


        def sorteio_faixa_velocidade(self):

            if self.esteira_ligada == True:

                if planta.proxima_mudanca_faixa == 0:
                    
                    numero = random.randint(1, 4)

                    planta.faixa = numero

                    planta.proxima_mudanca_faixa = 30

                if planta.proxima_mudanca_velocidade == 0:

                    if planta.faixa == 1:
                        numero = random.random(1.0, 1.25)
                        planta.velocidade = numero

                    elif planta.faixa == 2:
                        numero = random.random(1.25, 1.50)
                        planta.velocidade = numero

                    elif planta.faixa == 3:
                        numero = random.random(1.50, 1.75)
                        planta.velocidade = numero

                    else:
                        numero = random.random(1.75, 2.0)
                        planta.velocidade = numero  
                    
        def intervalo_pecas(self):

            self.intervalo = [12, 10, 8, 6]

            aux = planta.faixa - 1    
            planta.proxima_entrada_peca = self.intervalo[aux]

            
            pass

