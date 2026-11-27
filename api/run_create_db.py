"""Cria o banco SQLite. Rodar uma vez, a partir da raiz do projeto:

    python -m api.run_create_db
"""

import os
import sqlite3

import config


if __name__ == '__main__':

    os.makedirs(os.path.dirname(config.CAMINHO_DB), exist_ok=True)

    connection = sqlite3.connect(config.CAMINHO_DB)

    connection.execute(
        """
            CREATE TABLE IF NOT EXISTS amostra (
              id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
              data_hora TEXT NOT NULL,
              esteira_ligada INTEGER NOT NULL,
              velocidade REAL NOT NULL,
              temperatura REAL NOT NULL,
              producao_total INTEGER NOT NULL,
              pecas_aprovadas INTEGER NOT NULL,
              pecas_rejeitadas INTEGER NOT NULL
            );
        """
    )

    connection.execute(
        """
            CREATE TABLE IF NOT EXISTS alarme (
              id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
              data_hora TEXT NOT NULL,
              alarme TEXT NOT NULL,
              nivel TEXT NOT NULL,
              evento TEXT NOT NULL,
              mensagem TEXT NOT NULL
            );
        """
    )

    connection.commit()
    connection.close()

    print(f'Banco criado em {config.CAMINHO_DB}')