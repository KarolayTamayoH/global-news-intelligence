
import re
from urllib.request import Request, urlopen

INDEX_URL = "https://data.gdeltproject.org/gkg/index.html"


def get_available_files():
    request = Request(
        INDEX_URL,
        headers={"User-Agent": "GlobalNewsIntelligence/1.0"},
    )

    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
        print("HTTP status:", response.status)
        print("URL consultada:", response.url)

    # Busca los nombres de archivo en cualquier parte del índice.
    filenames = set(
        re.findall(r"\b(\d{8}\.gkg\.csv\.zip)\b", html)
    )

    return sorted(filenames, reverse=True)


if __name__ == "__main__":
    files = get_available_files()

    print(f"Archivos GKG encontrados: {len(files)}")

    for filename in files[:10]:
        print(" ", filename)

    if not files:
        print("No se encontraron archivos. Revisar la respuesta del índice.")
