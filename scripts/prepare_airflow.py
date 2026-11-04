"""Crear una clave local de metadata Airflow sin modificar .env ni imprimir secretos."""
import os
import secrets

from src.config import ROOT


def main():
    directory = ROOT / '.airflow'
    directory.mkdir(exist_ok=True)
    path = directory / 'local.env'
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print('Se conserva .airflow/local.env existente')
        return
    with os.fdopen(descriptor, 'w') as stream:
        stream.write(f'AIRFLOW_DB_PASSWORD={secrets.token_hex(24)}\n')
    print('Creado .airflow/local.env (ignorado por Git)')


if __name__ == '__main__':
    main()
