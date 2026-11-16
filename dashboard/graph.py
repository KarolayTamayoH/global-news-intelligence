"""Visualizacion de una muestra de relaciones sin dependencias de layout externas."""
from collections import Counter

import plotly.graph_objects as go

KINDS = [
    # tipo, etiqueta, color, posicion x, posicion del texto
    ('Theme', 'Temas', '#a78bfa', -1, 'middle left'),
    ('GKGRecord', 'Registros GKG', '#54b6ff', 0, 'top center'),
    ('Organization', 'Organizaciones', '#34d399', 1, 'middle right'),
]
EDGE_STYLES = {
    'HAS_THEME': ('Relación con tema', 'rgba(167,139,250,0.45)'),
    'MENTIONS_ORG': ('Relación con organización', 'rgba(52,211,153,0.45)'),
}


def _short(name, limit):
    return name if len(name) <= limit else name[:limit - 1] + '…'


def graph_figure(rows):
    groups = {'Theme': set(), 'GKGRecord': set(), 'Organization': set()}
    degree = Counter()
    for row in rows:
        groups['GKGRecord'].add(row['record_id'])
        if row.get('entity_type') in ('Theme', 'Organization') and row.get('entity_name'):
            groups[row['entity_type']].add(row['entity_name'])
            degree[('GKGRecord', row['record_id'])] += 1
            degree[(row['entity_type'], row['entity_name'])] += 1

    positions = {}
    for kind, _, _, x, _ in KINDS:
        names = sorted(groups[kind])
        for index, name in enumerate(names):
            positions[kind, name] = (x, 0 if len(names) == 1 else 1 - 2 * index / (len(names) - 1))

    # Aristas agrupadas por tipo de relacion para colorearlas de forma distinta.
    edges = {name: ([], []) for name in EDGE_STYLES}
    for row in rows:
        key = (row.get('entity_type'), row.get('entity_name'))
        relation = row.get('relationship')
        if key in positions and relation in edges:
            start, end = positions['GKGRecord', row['record_id']], positions[key]
            edges[relation][0].extend([start[0], end[0], None])
            edges[relation][1].extend([start[1], end[1], None])

    figure = go.Figure()
    for relation, (edge_x, edge_y) in edges.items():
        if not edge_x:
            continue
        label, color = EDGE_STYLES[relation]
        figure.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', name=label,
                                    line={'width': 1.2, 'color': color},
                                    hoverinfo='skip', showlegend=False))

    for kind, label, color, _, text_position in KINDS:
        names = sorted(groups[kind])
        if not names:
            continue
        sizes = [(14 if kind == 'GKGRecord' else 9) + min(degree[(kind, name)], 12) for name in names]
        figure.add_trace(go.Scatter(
            x=[positions[kind, name][0] for name in names],
            y=[positions[kind, name][1] for name in names], mode='markers+text', name=label,
            marker={'size': sizes, 'color': color, 'line': {'width': 1, 'color': '#0b1220'}},
            text=[_short(name, 12 if kind == 'GKGRecord' else 30) for name in names],
            textposition=text_position, textfont={'size': 11},
            customdata=[[name, degree[(kind, name)]] for name in names],
            hovertemplate=label + ': %{customdata[0]}<br>Conexiones en la muestra: %{customdata[1]}<extra></extra>'))

    figure.update_layout(template='plotly_dark', height=650,
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         margin={'l': 20, 'r': 20, 't': 35, 'b': 35},
                         xaxis={'visible': False, 'range': [-1.9, 1.9]},
                         yaxis={'visible': False, 'range': [-1.15, 1.15]},
                         legend={'orientation': 'h'}, hovermode='closest')
    return figure
