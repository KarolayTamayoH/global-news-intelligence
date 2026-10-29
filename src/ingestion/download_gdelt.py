#Descargar primero a un archivo temporal .part.
#Verificar que el ZIP sea íntegro y contenga un CSV GKG.
#Renombrar el archivo temporal únicamente cuando pase la validación.
import re
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

INDEX_URL = "https://data.gdeltproject.org/gkg/index.html"
BASE_URL = "https://data.gdeltproject.org/gkg/"

RAW_DIR = Path(__file__).resolve().parents[2] / "data/raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def get_available_files():
    request = Request(
        INDEX_URL,
        headers={"User-Agent": "GlobalNewsIntelligence/1.0"},
    )

    with urlopen(request, timeout=30) as response:
        html = response.read().decode(
            "utf-8", errors="replace"
        )

    return sorted(
        set(re.findall(r"\b(\d{8}\.gkg\.csv\.zip)\b", html)),
        reverse=True,
    )


def validate_zip(path, filename):
    expected_csv = filename.removesuffix(".zip")

    try:
        with zipfile.ZipFile(path) as archive:
            if archive.namelist() != [expected_csv]:
                return False

            if archive.testzip() is not None:
                return False

        return True

    except (zipfile.BadZipFile, OSError):
        return False


def download_file(filename):
    if not re.fullmatch(r"\d{8}\.gkg\.csv\.zip", filename):
        raise ValueError(f"Nombre de archivo invalido: {filename}")

    destination = RAW_DIR / filename
    temporary = RAW_DIR / f"{filename}.part"

    if destination.exists():
        if validate_zip(destination, filename):
            print(f"Archivo valido, se omite: {filename}")
            return destination

        print(f"Archivo local invalido: {filename}")
        destination.unlink()

    url = BASE_URL + filename

    request = Request(
        url,
        headers={"User-Agent": "GlobalNewsIntelligence/1.0"},
    )

    print(f"Descargando: {filename}")

    try:
        with urlopen(request, timeout=120) as response:
            with temporary.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)

                    if not chunk:
                        break

                    output.write(chunk)

        if not validate_zip(temporary, filename):
            raise ValueError(
                f"El archivo descargado no es valido: {filename}"
            )

        temporary.replace(destination)

        print(f"Descarga verificada: {filename}")
        print(f"Tamano: {destination.stat().st_size:,} bytes")

        return destination

    finally:
        if temporary.exists():
            temporary.unlink()


if __name__ == "__main__":
    files = get_available_files()

    if not files:
        raise RuntimeError("No se encontraron archivos GKG.")

    download_file(files[0])
