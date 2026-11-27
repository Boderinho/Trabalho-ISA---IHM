LIMITE_ALERTA = 80.0
LIMITE_CRITICO = 100.0
LIMITE_RELIGAR = 70.0
REJEICAO_MAX = 10.0      # %
MIN_PECAS = 20


class Regras:

    def __init__(self):
        self.alarmes_ativos = set()
        self.desligada_temperatura = False

    def dados(self, dados):

        temperatura = dados["temperatura"]
        ligada = dados["esteira_ligada"]
        total = dados["producao_total"]
        reijeitadas = dados["pecas_rejeitadas"]

        comando = None
        ativos = set()


        limite = LIMITE_ALERTA - 2 if 'temperatura_elevada' in self.alarmes_ativos else LIMITE_ALERTA

        if temperatura > limite:
            ativos.add('temperatura_elevada') 

        if temperatura > LIMITE_CRITICO or self.desligada_temperatura:
            ativos.add('temperatura_critica')
            if ligada:
                comando = False
                self.desligada_temperatura = True

        if self.desligada_temperatura and not ligada and temperatura < LIMITE_RELIGAR:
            comando = True
            self.desligada_temperatura = False

        if not ligada:
            ativos.add('esteira_parada')

        if total >= MIN_PECAS and 100*reijeitadas/total > REJEICAO_MAX:
            ativos.add('rejeicao_alta')

        mudancas = [("ativo", a) for a in sorted(ativos - self.alarmes_ativos)]
        mudancas += [("normalizado", a) for a in sorted(self.alarmes_ativos - ativos)]
        self.alarmes_ativos = ativos
        
        return comando, mudancas