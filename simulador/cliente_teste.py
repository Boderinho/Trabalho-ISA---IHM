"""Cliente de teste do servidor Modbus (estilo da prática da disciplina).

Lê as seis variáveis com UMA requisição por ciclo e permite ligar ou
desligar a esteira. A lógica de leitura vai virar api/modbus_client.py.

Execução (com o servidor rodando, a partir da raiz do projeto):
    python -m simulador.cliente_teste
    python -m simulador.cliente_teste desligar
    python -m simulador.cliente_teste ligar
"""

import sys
import time
from datetime import datetime

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import decode_ieee, word_list_to_long

import config


class ClienteModbusTCP:

    def __init__(self, endereco_servidor: str, numero_porta: int):
        self.cliente = ModbusClient(host=endereco_servidor, port=numero_porta)

    @staticmethod
    def _float32(words: list) -> float:
        return decode_ieee(word_list_to_long(words)[0])

    def ler_variaveis(self):
        """Uma leitura do bloco = um passo da simulação. Retorna None se falhar."""
        regs = self.cliente.read_holding_registers(config.REG_INICIO, config.QTD_REGS)
        bobina = self.cliente.read_coils(config.COIL_ESTEIRA, 1)

        if regs is None or bobina is None:
            return None

        # Os endereços do mapa são absolutos; o bloco começa em REG_INICIO
        def pos(endereco):
            return endereco - config.REG_INICIO

        return {
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'esteira_ligada': bobina[0],
            'velocidade': self._float32(regs[pos(config.REG_VELOCIDADE):pos(config.REG_VELOCIDADE) + 2]),
            'temperatura': self._float32(regs[pos(config.REG_TEMPERATURA):pos(config.REG_TEMPERATURA) + 2]),
            'producao_total': regs[pos(config.REG_TOTAL)],
            'pecas_aprovadas': regs[pos(config.REG_APROVADAS)],
            'pecas_rejeitadas': regs[pos(config.REG_REJEITADAS)],
        }

    def comandar_esteira(self, ligada: bool) -> bool:
        return bool(self.cliente.write_single_coil(config.COIL_ESTEIRA, ligada))

    def close(self):
        self.cliente.close()


if __name__ == '__main__':

    cliente = ClienteModbusTCP(config.MODBUS_HOST, config.MODBUS_PORTA)

    if len(sys.argv) > 1 and sys.argv[1] in ('ligar', 'desligar'):
        ok = cliente.comandar_esteira(sys.argv[1] == 'ligar')
        print('Comando enviado.' if ok else 'Falha ao enviar o comando.')
        cliente.close()
        sys.exit(0)

    print('\nLendo dados do servidor ... (Ctrl+C para encerrar)')

    try:
        while True:
            dados = cliente.ler_variaveis()

            if dados is None:
                c = cliente.cliente
                print(f'\nFalha na leitura: {c.last_error_as_txt} -- {c.last_except_as_txt}')
            else:
                print(f'\nDados: {dados}')

            time.sleep(2)
    except KeyboardInterrupt:
        print('\nEncerrando cliente ...')
    finally:
        cliente.close()