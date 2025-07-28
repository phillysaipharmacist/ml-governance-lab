"""
load_to_postgres.py

Load evaluation metrics and drift reports into PostgreSQL.
"""
import json, os, sys

def load_password() -> str:
        path = os.environ.get('DATABASE_PASSWORD_FILE')
        if path and os.path.isfile(path):
            return open(path).read().strip()
        raise RuntimeError('DATABASE_PASSWORD_FILE is not set or file missing')

def load_metrics(cursor, table: str, json_path: str):
        if not os.path.exists(json_path):
            print(f"File {json_path} not found; skipping load for {table}.")
            return
        with open(json_path) as f:
            data = json.load(f)
        cursor.execute(f"INSERT INTO {table} (data) VALUES (%s)", (json.dumps(data),))

def main() -> int:
        try: import psycopg2
        except ImportError:
            print("psycopg2 is not installed; cannot load results to PostgreSQL.", file=sys.stderr)
            return 1
        user = os.environ.get('DATABASE_USER','ml_user')
        dbname = os.environ.get('DATABASE_NAME','ml_db')
        password = load_password()
        host = os.environ.get('DATABASE_HOST','db')
        port = int(os.environ.get('DATABASE_PORT','5432'))
        try:
            conn = psycopg2.connect(database=dbname,user=user,password=password,host=host,port=port)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS model_metrics (id SERIAL PRIMARY KEY, data JSONB);")
            cur.execute("CREATE TABLE IF NOT EXISTS seismometer_results (id SERIAL PRIMARY KEY, data JSONB);")
            cur.execute("CREATE TABLE IF NOT EXISTS drift_reports (id SERIAL PRIMARY KEY, data JSONB);")
            models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
            load_metrics(cur,'model_metrics',os.path.join(models_dir,'metrics.json'))
            load_metrics(cur,'seismometer_results',os.path.join(models_dir,'seismometer.json'))
            load_metrics(cur,'drift_reports',os.path.join(models_dir,'drift.json'))
            cur.close()
            print("Results loaded to PostgreSQL.")
            return 0
        except Exception as e:
            print(f"Error loading results to PostgreSQL: {e}", file=sys.stderr)
            return 1
        finally:
            if conn: conn.close()

if __name__ == '__main__':
        sys.exit(main())