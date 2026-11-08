"""Visualizacion de una muestra de relaciones sin dependencias de layout externas."""
import plotly.graph_objects as go


def graph_figure(rows):
    groups = {'Theme': set(), 'GKGRecord': set(), 'Organization': set()}
    for row in rows:
        groups['GKGRecord'].add(row['record_id'])
        if row.get('entity_type') in ('Theme', 'Organization') and row.get('entity_name'):
            groups[row['entity_type']].add(row['entity_name'])
    positions = {}
    for kind, x in [('Theme', -1), ('GKGRecord', 0), ('Organization', 1)]:
        names = sorted(groups[kind])
        for index, name in enumerate(names):
            positions[kind, name] = (x, 0 if len(names) == 1 else 1 - 2 * index / (len(names) - 1))
    edge_x, edge_y = [], []
    for row in rows:
        key = (row.get('entity_type'), row.get('entity_name'))
        if key in positions:
            start, end = positions['GKGRecord', row['record_id']], positions[key]
            edge_x.extend([start[0], end[0], None])
            edge_y.extend([start[1], end[1], None])
    figure = go.Figure(go.Scatter(x=edge_x, y=edge_y, mode='lines',
                                line={'width': 1, 'color': '#62718b'},
                                hoverinfo='skip', showlegend=False))
    for kind, label, color in [('Theme', 'Temas', '#a78bfa'),
                               ('GKGRecord', 'Registros GKG', '#54b6ff'),
                               ('Organization', 'Organizaciones', '#34d399')]:
        names = sorted(groups[kind])
        if not names:
            continue
        figure.add_trace(go.Scatter(
            x=[positions[kind, name][0] for name in names],
            y=[positions[kind, name][1] for name in names], mode='markers+text', name=label,
            marker={'size': 13 if kind == 'GKGRecord' else 9, 'color': color},
            text=[name[:12] if kind == 'GKGRecord' else name[:24] for name in names],
            textposition='top center', customdata=names,
            hovertemplate=label + ': %{customdata}<extra></extra>'))
    figure.update_layout(template='plotly_dark', height=650,
                         margin={'l': 90, 'r': 90, 't': 35, 'b': 35},
                         xaxis={'visible': False, 'range': [-1.5, 1.5]},
                         yaxis={'visible': False, 'range': [-1.15, 1.15]},
                         legend={'orientation': 'h'}, hovermode='closest')
    return figure
