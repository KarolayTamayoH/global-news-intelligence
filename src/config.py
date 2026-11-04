"""Configuración del proceso. Cargar .env en el shell antes de ejecutar Python."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def port(name, default):
    value = int(os.getenv(name, str(default)))
    if not 1 <= value <= 65535:
        raise ValueError(f'{name} debe estar entre 1 y 65535')
    return value


MONGO_URI = os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27018/')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'global_news')
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', '127.0.0.1')
CASSANDRA_PORT = port('CASSANDRA_PORT', 9043)
CASSANDRA_KEYSPACE = os.getenv('CASSANDRA_KEYSPACE', 'global_news_analytics')
# El bootstrap interpola este identificador en el DDL versionado.
if not re.fullmatch(r'[a-z][a-z0-9_]{0,47}', CASSANDRA_KEYSPACE):
    raise ValueError('CASSANDRA_KEYSPACE debe ser un identificador CQL en minusculas')
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://127.0.0.1:7688')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')
DATA_DIR = Path(os.getenv('GNI_DATA_DIR', str(ROOT / 'data'))).expanduser()
if not DATA_DIR.is_absolute():
    DATA_DIR = ROOT / DATA_DIR
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
