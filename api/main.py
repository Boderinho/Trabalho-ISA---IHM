"""Web service da planta (FastAPI).

Fica entre o servidor Modbus e as IHMs. Só o endpoint /ler_variaveis avança
a simulação (cada chamada lê o bloco no Modbus uma vez). Os demais endpoints
só consultam o banco ou comandam a esteira.

Modo de operação (variável de ambiente MODO, padrão "streamlit"):
    streamlit  as regras de automação rodam aqui
    scada      só entrega dados; as regras ficam no ScadaBR
"""

import uvicorn

from datetime import datetime
from threading import Lock

from fastapi import FastAPI
from pydantic import BaseModel

import config
from api.modbus_client import ClienteModbusTCP
from api.planta_dao import PlantaDAO
from api.regras import Regras, LIMITE_ALERTA, LIMITE_CRITICO, REJEICAO_MAX

app = FastAPI()


class ComandoEsteira(BaseModel):
    ligada: bool


NIVEIS = {
    'temperatura_elevada': 'aviso',
    'temperatura_critica': 'critico',
    'esteira_parada': 'informativo',
    'rejeicao_alta': 'aviso',
}

MENSAGENS = {
    'temperatura_elevada': f'Temperatura do motor acima de {LIMITE_ALERTA:.0f} °C',
    'temperatura_critica': f'Temperatura acima de {LIMITE_CRITICO:.0f} °C: esteira desligada',
    'esteira_parada': 'Esteira parada',
    'rejeicao_alta': f'Taxa de rejeição acima de {REJEICAO_MAX:.0f}%',
}

cliente_modbus = ClienteModbusTCP(config.MODBUS_HOST, config.MODBUS_PORTA)
planta_dao = PlantaDAO(caminho_db=config.CAMINHO_DB)
regras = Regras()

# Protege o conjunto leitura + regras + gravação, já que as consultas das
# IHMs chegam em threads diferentes.
trava = Lock()


def agora() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@app.get('/')
def init():
    return f'Web Service da Planta (modo: {config.MODO})'


@app.get('/ler_variaveis')
def ler_variaveis():
    with trava:
        dados = cliente_modbus.ler_variaveis()
        if dados is None:
            return {
                'Erro': f'Falha na leitura do servidor Modbus: {cliente_modbus.ultimo_erro()}'
            }

        data_hora = agora()
        planta_dao.cadastrar_amostra(data_hora, dados)

        if config.MODO == 'streamlit':
            comando, mudancas = regras.dados(dados)

            for evento, alarme in mudancas:
                planta_dao.cadastrar_alarme(
                    data_hora, alarme, NIVEIS[alarme], evento, MENSAGENS[alarme])

            # O comando vale a partir da próxima leitura
            if comando is not None:
                cliente_modbus.comandar_esteira(comando)

        resposta = dict(dados)
        resposta['data_hora'] = data_hora
        resposta['alarmes_ativos'] = sorted(regras.alarmes_ativos) if config.MODO == 'streamlit' else []
        return resposta


@app.get('/listar_amostras')
def listar_amostras(limite: int = 100):
    limite = max(1, min(limite, 5000))
    amostras = planta_dao.listar_amostras(limite)
    return [
        {
            'data_hora': a[0],
            'esteira_ligada': bool(a[1]),
            'velocidade': a[2],
            'temperatura': a[3],
            'producao_total': a[4],
            'pecas_aprovadas': a[5],
            'pecas_rejeitadas': a[6],
        }
        for a in amostras
    ]


@app.get('/listar_alarmes')
def listar_alarmes(limite: int = 50):
    limite = max(1, min(limite, 1000))
    alarmes = planta_dao.listar_alarmes(limite)
    return [
        {
            'data_hora': a[0],
            'alarme': a[1],
            'nivel': a[2],
            'evento': a[3],
            'mensagem': a[4],
        }
        for a in alarmes
    ]


@app.get('/alarmes_ativos')
def alarmes_ativos():
    if config.MODO != 'streamlit':
        return []
    return [
        {'alarme': a, 'nivel': NIVEIS[a], 'mensagem': MENSAGENS[a]}
        for a in sorted(regras.alarmes_ativos)
    ]


@app.post('/comandar_esteira')
def comandar_esteira(comando: ComandoEsteira):
    with trava:
        if not cliente_modbus.comandar_esteira(comando.ligada):
            return {
                'Erro': f'Falha ao enviar o comando ao servidor Modbus: {cliente_modbus.ultimo_erro()}'
            }
        # Comando do operador: a regra de temperatura não deve desfazê-lo depois
        regras.desligada_temperatura = False
    return {'esteira_ligada': comando.ligada}


if __name__ == '__main__':

    uvicorn.run('api.main:app', port=config.API_PORTA, log_level='info',
                reload=True)