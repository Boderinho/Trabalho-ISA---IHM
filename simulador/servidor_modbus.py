"""Servidor Modbus/TCP da planta.

Cada leitura do bloco de holding registers avança a planta em um passo
(tick). Quem lê precisa pedir o bloco inteiro em UMA requisição
(endereço 0, 7 registradores), senão cada requisição avança um passo.

Nesta etapa do versionamento, é necessário utilizar dois terminais da raiz do projeto
para executar o cliente e o servidor.

Comece pelo servidor
"python -m servidor_modbus.py"

E depois pelo cliente
"python -m cliente_teste.py"
"""

import time
from datetime import datetime
from threading import Lock

from pyModbusTCP.constants import EXP_ILLEGAL_FUNCTION
from pyModbusTCP.server import DataBank, DataHandler, ModbusServer
from pyModbusTCP.utils import encode_ieee, long_list_to_word

import config
from simulador.planta import Planta

MAX_REGISTRADOR = 0xFFFF


def float32_para_words(valor: float) -> list:
    """REAL -> 2 registradores (mesmo método da prática)."""
    return long_list_to_word([encode_ieee(valor)])


class ManipuladorPlanta(DataHandler):
    """Liga o ModbusServer à planta.

    - Leitura do bloco de holding registers: avança um passo e publica.
    - Escrita no coil da esteira: repassa o comando à planta.
    - Escrita nos holding registers: recusada (são variáveis de processo).
    """

    def __init__(self, planta: Planta, verboso: bool = True):
        super().__init__(data_bank=DataBank())
        self.planta = planta
        self.verboso = verboso
        # Várias conexões são atendidas em threads: o lock evita que dois
        # clientes avancem ou leiam a planta ao mesmo tempo.
        self.lock = Lock()
        self._publicar()

    def _publicar(self):
        """Copia o estado atual da planta para o data bank."""
        v = self.planta.obter_variaveis()
        banco = self.data_bank

        banco.set_coils(config.COIL_ESTEIRA, [v["esteira_ligada"]])
        banco.set_holding_registers(config.REG_VELOCIDADE,
                                    float32_para_words(v["velocidade"]))
        banco.set_holding_registers(config.REG_TEMPERATURA,
                                    float32_para_words(v["temperatura"]))
        banco.set_holding_registers(config.REG_TOTAL,
                                    [min(v["producao_total"], MAX_REGISTRADOR)])
        banco.set_holding_registers(config.REG_APROVADAS,
                                    [min(v["pecas_aprovadas"], MAX_REGISTRADOR)])
        banco.set_holding_registers(config.REG_REJEITADAS,
                                    [min(v["pecas_rejeitadas"], MAX_REGISTRADOR)])

    def _registrar(self):
        v = self.planta.obter_variaveis()
        print(f"[{datetime.now():%H:%M:%S}] "
              f"esteira={'ligada' if v['esteira_ligada'] else 'desligada':9} "
              f"vel={v['velocidade']:.2f} m/s  temp={v['temperatura']:.1f} °C  "
              f"total={v['producao_total']}  "
              f"aprov={v['pecas_aprovadas']}  rej={v['pecas_rejeitadas']}")

    @staticmethod
    def _toca_bloco(address: int, count: int) -> bool:
        fim_bloco = config.REG_INICIO + config.QTD_REGS
        return address < fim_bloco and address + count > config.REG_INICIO

    def read_h_regs(self, address, count, srv_info):
        with self.lock:
            if self._toca_bloco(address, count):
                self.planta.tick()
                self._publicar()
                if self.verboso:
                    self._registrar()
            return super().read_h_regs(address, count, srv_info)

    def write_coils(self, address, bits_l, srv_info):
        with self.lock:
            if address <= config.COIL_ESTEIRA < address + len(bits_l):
                self.planta.definir_esteira(bits_l[config.COIL_ESTEIRA - address])
                if self.verboso:
                    estado = "LIGAR" if bits_l[config.COIL_ESTEIRA - address] else "DESLIGAR"
                    print(f"[{datetime.now():%H:%M:%S}] comando recebido: {estado} esteira")
            resposta = super().write_coils(address, bits_l, srv_info)
            # Desligar zera a velocidade na hora; publica sem avançar a planta.
            self._publicar()
            return resposta

    def write_h_regs(self, address, words_l, srv_info):
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)


class ServidorModbusTCP:

    def __init__(self, endereco_servidor: str, numero_porta: int, verboso: bool = True):
        self.planta = Planta()
        self.server = ModbusServer(
            host=endereco_servidor,
            port=numero_porta,
            no_block=True,
            data_hdl=ManipuladorPlanta(self.planta, verboso=verboso),
        )

    def run(self):
        print('\nIniciando servidor ...')

        # start() não devolve valor: se a porta estiver ocupada, levanta NetworkError
        try:
            self.server.start()
        except ModbusServer.NetworkError as erro:
            raise RuntimeError(
                f'Não foi possível iniciar o servidor em '
                f'{self.server.host}:{self.server.port} ({erro})') from erro

        print('\nServidor em execução ... (Ctrl+C para encerrar)')

        try:
            # Sem laço de simulação: a planta só avança nas leituras.
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nEncerrando servidor ...')
        finally:
            self.server.stop()


if __name__ == '__main__':

    servidor = ServidorModbusTCP(
        endereco_servidor=config.MODBUS_HOST,
        numero_porta=config.MODBUS_PORTA,
    )

    servidor.run()