"""Compatibilidad CLI: publicar todos los KPIs de cada fecha en una versión."""
from src.transformation.aggregate_snapshot import aggregate_snapshot


def aggregate_daily(target_date=None):
    return aggregate_snapshot(target_date)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', help='Particion YYYYMMDD; por defecto todas las fechas')
    aggregate_daily(parser.parse_args().date)
