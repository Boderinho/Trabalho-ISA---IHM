"""Cliente Modbus usado pelo web service (base: simulador/cliente_teste.py).

Os endpoints do FastAPI rodam em threads. O lock garante que uma leitura
do bloco (que avança um passo da planta) não se misture com outra.
"""

from threading import Lock

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import decode_ieee, word_list_to_long

import config


class ClienteModbusTCP:

    def __init__(self, endereco_servidor: str, numero_porta: int):
        self.cliente = ModbusClient(
            host=endereco_servidor,
            port=numero_porta,
            timeout=2,
        )
        self.lock = Lock()

    @staticmethod
    def _float32(words: list) -> float:
        return decode_ieee(word_list_to_long(words)[0])

    def ler_variaveis(self):
        """Uma leitura do bloco = um passo da simulação. Retorna None se falhar."""
        with self.lock:
            regs = self.cliente.read_holding_registers(config.REG_INICIO, config.QTD_REGS)
            bobina = self.cliente.read_coils(config.COIL_ESTEIRA, 1)

        if regs is None or bobina is None:
            return None

        def pos(endereco):
            return endereco - config.REG_INICIO

        velocidade = self._float32(regs[pos(config.REG_VELOCIDADE):pos(config.REG_VELOCIDADE) + 2])
        temperatura = self._float32(regs[pos(config.REG_TEMPERATURA):pos(config.REG_TEMPERATURA) + 2])

        return {
            'esteira_ligada': bobina[0],
            'velocidade': round(velocidade, 2),
            'temperatura': round(temperatura, 2),
            'producao_total': regs[pos(config.REG_TOTAL)],
            'pecas_aprovadas': regs[pos(config.REG_APROVADAS)],
            'pecas_rejeitadas': regs[pos(config.REG_REJEITADAS)],
        }

    def comandar_esteira(self, ligada: bool) -> bool:
        with self.lock:
            return bool(self.cliente.write_single_coil(config.COIL_ESTEIRA, ligada))

    def ultimo_erro(self) -> str:
        return f'{self.cliente.last_error_as_txt} -- {self.cliente.last_except_as_txt}'

    def close(self):
        self.cliente.close()