"""Compatibilidad CLI: entidades y métricas se publican conjuntamente."""
from src.transformation.aggregate_snapshot import aggregate_snapshot


def aggregate_entities(target_date=None):
    return aggregate_snapshot(target_date)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', help='Particion YYYYMMDD; por defecto todas las fechas')
    aggregate_entities(parser.parse_args().date)
