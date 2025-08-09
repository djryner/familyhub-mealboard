"""Simple migration runner executing SQL files in migrations/ directory."""
from pathlib import Path
from sqlalchemy import create_engine, text
from config import get_settings


def main():
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    mig_dir = Path(__file__).resolve().parent.parent / 'migrations'
    for path in sorted(mig_dir.glob('*.sql')):
        with engine.begin() as conn, open(path, 'r', encoding='utf-8') as f:
            conn.connection.executescript(f.read())
            print(f'Applied {path.name}')


if __name__ == '__main__':
    main()
