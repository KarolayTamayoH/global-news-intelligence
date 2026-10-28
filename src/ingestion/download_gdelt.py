import re
from pathlib import Path
from urllib.request import Request, urlopen

INDEX_URL = "https://data.gdeltproject.org/gkg/index.html"
BASE_URL = "https://data.gdeltproject.org/gkg/"

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def get_available_files():
    request = Request(
        INDEX_URL,
        headers={"User-Agent": "GlobalNewsIntelligence/1.0"},
    )

    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")

    return sorted(
        set(re.findall(r"\b(\d{8}\.gkg\.csv\.zip)\b", html)),
        reverse=True,
    )


def download_file(filename):
    destination = RAW_DIR / filename

    if destination.exists() and destination.stat().st_size > 0:
        print(f"Ya existe, se omite: {filename}")
        return

    url = BASE_URL + filename
    request = Request(
        url,
        headers={"User-Agent": "GlobalNewsIntelligence/1.0"},
    )

    print(f"Descargando: {filename}")

    with urlopen(request, timeout=120) as response:
        content = response.read()

    destination.write_bytes(content)
    print(f"Descargado: {filename} ({destination.stat().st_size:,} bytes)")


if __name__ == "__main__":
    files = get_available_files()

    if not files:
        raise RuntimeError("No se encontraron archivos GKG.")

    # Por ahora descargamos solo el archivo diario más reciente.
    download_file(files[0])