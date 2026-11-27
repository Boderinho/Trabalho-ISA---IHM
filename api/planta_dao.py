import sqlite3


class PlantaDAO:

    def __init__(self, caminho_db: str) -> None:
        self.caminho_db = caminho_db

    def cadastrar_amostra(self, data_hora: str, dados: dict):
        connection = sqlite3.connect(self.caminho_db)
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO amostra (data_hora, esteira_ligada, velocidade, temperatura,
                                    producao_total, pecas_aprovadas, pecas_rejeitadas)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data_hora, int(dados['esteira_ligada']), dados['velocidade'],
             dados['temperatura'], dados['producao_total'],
             dados['pecas_aprovadas'], dados['pecas_rejeitadas'])
        )
        connection.commit()
        id_amostra = cursor.lastrowid
        connection.close()
        return id_amostra

    def listar_amostras(self, limite: int):
        """Últimas amostras, em ordem cronológica (da mais antiga para a mais nova)."""
        connection = sqlite3.connect(self.caminho_db)
        cursor = connection.cursor()
        cursor.execute(
            """SELECT data_hora, esteira_ligada, velocidade, temperatura,
                      producao_total, pecas_aprovadas, pecas_rejeitadas
               FROM amostra ORDER BY id DESC LIMIT ?""",
            (limite,)
        )
        lista_amostras = cursor.fetchall()
        connection.close()
        return lista_amostras[::-1]

    def cadastrar_alarme(self, data_hora: str, alarme: str, nivel: str,
                         evento: str, mensagem: str):
        connection = sqlite3.connect(self.caminho_db)
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO alarme (data_hora, alarme, nivel, evento, mensagem)
               VALUES (?, ?, ?, ?, ?)""",
            (data_hora, alarme, nivel, evento, mensagem)
        )
        connection.commit()
        id_alarme = cursor.lastrowid
        connection.close()
        return id_alarme

    def listar_alarmes(self, limite: int):
        """Últimos alarmes, do mais novo para o mais antigo."""
        connection = sqlite3.connect(self.caminho_db)
        cursor = connection.cursor()
        cursor.execute(
            """SELECT data_hora, alarme, nivel, evento, mensagem
               FROM alarme ORDER BY id DESC LIMIT ?""",
            (limite,)
        )
        lista_alarmes = cursor.fetchall()
        connection.close()
        return lista_alarmes