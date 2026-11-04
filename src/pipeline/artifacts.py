"""Artefactos en el directorio local compartido; XCom solo transporta sus URI."""
import os
import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse

from src.config import DATA_DIR


class ArtifactStore:
    def __init__(self, base_uri=None):
        self.base_uri = (base_uri or os.getenv('GNI_ARTIFACT_URI') or DATA_DIR.as_uri()).rstrip('/')
        parsed = urlparse(self.base_uri)
        if (parsed.scheme != 'file' or parsed.netloc or not parsed.path.startswith('/')
                or parsed.query or parsed.fragment):
            raise ValueError('GNI_ARTIFACT_URI debe ser file:///ruta/absoluta/local')

    def uri(self, key):
        parts = key.split('/')
        if (not key or unquote(key) != key or any(char in key for char in ('?', '#', '\\'))
                or any(part in ('', '.', '..') for part in parts)):
            raise ValueError('Clave de artefacto invalida')
        return f'{self.base_uri}/{key}'

    def publish(self, source, key):
        uri = self.uri(key)
        destination = Path(unquote(urlparse(uri).path))
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + '.part')
        try:
            shutil.copyfile(source, temporary)
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
        return uri

    def fetch(self, uri, destination):
        # Solo aceptar artefactos del prefijo configurado.
        if not uri.startswith(self.base_uri + '/'):
            raise ValueError('Artefacto fuera del almacenamiento configurado')
        key = uri[len(self.base_uri) + 1:]
        self.uri(key)
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(unquote(urlparse(uri).path)), destination)
        return destination
