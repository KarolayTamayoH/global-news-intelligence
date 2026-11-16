"""Iconos SVG en linea (estilo Lucide, licencia ISC), marca propia y diagrama del DAG.

Todo se entrega como <img> con data URI, de modo que Streamlit no lo sanea.
Los logos PNG son opcionales: si existe dashboard/assets/<nombre>.png se usa; si no, se usa un icono.
"""
import base64
from functools import lru_cache
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"

ICONS = {
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    "server": '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>',
    "activity": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "trending-up": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "trending-down": '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>',
    "hash": '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "file-text": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>',
    "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "tag": '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "percent": '<line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "bar-chart": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "filter": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
}


def _uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@lru_cache(maxsize=256)
def icon(name, size=20, color="#9ec5ff", stroke=1.8):
    """Devuelve un <img> con el icono SVG como data URI. El color debe ser hexadecimal."""
    body = ICONS.get(name, ICONS["info"])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
           f'fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" '
           f'stroke-linejoin="round">{body}</svg>')
    return (f'<img src="{_uri(svg)}" width="{size}" height="{size}" '
            f'alt="" style="vertical-align:middle">')


@lru_cache(maxsize=32)
def asset_uri(name):
    """Data URI del PNG dashboard/assets/<name>.png, o None si no existe."""
    path = ASSETS / f"{name}.png"
    if not path.is_file():
        return None
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def mark(name, fallback_icon, size=20, color="#9ec5ff"):
    """Logo PNG si existe; si no, el icono de respaldo."""
    uri = asset_uri(name)
    if uri:
        return (f'<img src="{uri}" height="{size}" alt="{name}" '
                f'style="vertical-align:middle;max-width:{size * 4}px;object-fit:contain">')
    return icon(fallback_icon, size, color)


# ---------------------------------------------------------------------------
# Marca propia: un globo cuyos meridianos son, a la vez, una red de nodos.
# ---------------------------------------------------------------------------
@lru_cache(maxsize=8)
def brand_mark(size=72):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#5fb0ff"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>'
        '<radialGradient id="bg" cx="0.3" cy="0.25" r="1"><stop offset="0" stop-color="#16294a"/>'
        '<stop offset="1" stop-color="#0b1426"/></radialGradient></defs>'
        '<rect width="96" height="96" rx="24" fill="url(#bg)" stroke="#2a3f66" stroke-width="1.5"/>'
        # esfera y meridianos
        '<g fill="none" stroke="url(#g)" stroke-width="2" stroke-linecap="round">'
        '<circle cx="48" cy="48" r="30"/>'
        '<ellipse cx="48" cy="48" rx="13" ry="30" opacity="0.55"/>'
        '<path d="M19 38h58M19 58h58" opacity="0.35"/></g>'
        # red de nodos sobre el globo
        '<g stroke="#e8eef8" stroke-width="1.6" stroke-linecap="round" opacity="0.9">'
        '<line x1="48" y1="48" x2="30" y2="34"/><line x1="48" y1="48" x2="68" y2="32"/>'
        '<line x1="48" y1="48" x2="72" y2="58"/><line x1="48" y1="48" x2="36" y2="70"/>'
        '<line x1="68" y1="32" x2="72" y2="58"/></g>'
        '<circle cx="30" cy="34" r="4" fill="#5fb0ff"/><circle cx="68" cy="32" r="4" fill="#5fb0ff"/>'
        '<circle cx="72" cy="58" r="4" fill="#34d399"/><circle cx="36" cy="70" r="4" fill="#f59e0b"/>'
        '<circle cx="48" cy="48" r="7" fill="#e8eef8"/><circle cx="48" cy="48" r="3" fill="#7c5cf0"/>'
        '</svg>')
    return f'<img src="{_uri(svg)}" width="{size}" height="{size}" alt="Global News Intelligence">'


# ---------------------------------------------------------------------------
# Diagrama del DAG de Airflow (misma topologia que el flujo real).
# ---------------------------------------------------------------------------
_PHASES = {
    "Ingesta": "#4f9cf9",
    "Transformación": "#a78bfa",
    "Carga": "#34d399",
    "Resultado": "#f59e0b",
}


@lru_cache(maxsize=2)
def pipeline_diagram():
    mono = "Consolas, Menlo, 'DejaVu Sans Mono', monospace"
    sans = "'Segoe UI', Arial, sans-serif"
    # (tarea, descripcion, x, centro_y, ancho, fase)
    nodes = [
        ("select_partition", "Elige la fecha", 10, 130, 140, "Ingesta"),
        ("extract", "Descarga GKG", 178, 130, 140, "Ingesta"),
        ("validate", "Control de calidad", 346, 130, 140, "Ingesta"),
        ("transform", "Normaliza datos", 514, 130, 140, "Transformación"),
        ("load_mongodb", "Carga documentos", 682, 130, 140, "Carga"),
        ("load_neo4j", "Carga el grafo", 872, 60, 160, "Carga"),
        ("aggregate_cassandra", "Calcula KPIs diarios", 872, 200, 160, "Carga"),
        ("generate_indicators", "Publica 6 indicadores", 1076, 130, 170, "Resultado"),
    ]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1260 300" width="1260" height="300">',
           '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
           'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#6b7d9c"/></marker></defs>']
    # conexiones
    edge = 'fill="none" stroke="#6b7d9c" stroke-width="1.6" marker-end="url(#ar)"'
    for a, b in zip(nodes[:4], nodes[1:5]):
        out.append(f'<line x1="{a[2] + a[4]}" y1="130" x2="{b[2] - 2}" y2="130" {edge}/>')
    out.append(f'<path d="M822 130 C847 130 847 60 870 60" {edge}/>')
    out.append(f'<path d="M822 130 C847 130 847 200 870 200" {edge}/>')
    out.append(f'<path d="M1032 60 C1054 60 1054 130 1074 130" {edge}/>')
    out.append(f'<path d="M1032 200 C1054 200 1054 130 1074 130" {edge}/>')
    out.append(f'<text x="952" y="134" text-anchor="middle" font-family="{sans}" font-size="11" '
               f'fill="#8b9bb4" font-style="italic">en paralelo</text>')
    # nodos
    for name, desc, x, cy, w, phase in nodes:
        color = _PHASES[phase]
        y = cy - 31
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="62" rx="10" fill="#111a2b" '
                   f'stroke="{color}" stroke-opacity="0.55" stroke-width="1.4"/>')
        out.append(f'<rect x="{x}" y="{y + 12}" width="4" height="38" rx="2" fill="{color}"/>')
        out.append(f'<text x="{x + 16}" y="{cy - 3}" font-family="{mono}" font-size="12" '
                   f'font-weight="700" fill="#e8eef8">{name}</text>')
        out.append(f'<text x="{x + 16}" y="{cy + 15}" font-family="{sans}" font-size="11" '
                   f'fill="#8b9bb4">{desc}</text>')
    # leyenda de fases
    lx = 10
    for label, color in _PHASES.items():
        out.append(f'<circle cx="{lx + 5}" cy="282" r="5" fill="{color}"/>')
        out.append(f'<text x="{lx + 16}" y="286" font-family="{sans}" font-size="12" fill="#a9b8cd">{label}</text>')
        lx += 36 + len(label) * 7.5
    out.append('</svg>')
    svg = "".join(out)
    return f'<img src="{_uri(svg)}" style="width:100%;height:auto;display:block" alt="Flujo del DAG en Airflow">'