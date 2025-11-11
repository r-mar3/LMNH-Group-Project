import pyodbc
from os import environ
from dotenv import load_dotenv


def load_schema_file() -> str:
    with open('schema.sql', 'r') as f:
        schema_text = f.read()
    return schema_text


def get_db_connection() -> pyodbc.Connection:
    load_dotenv()
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={environ['DB_HOST']}, {environ['DB_PORT']};'
        f'DATABASE={environ['DB_NAME']};'
        f'UID={environ['DB_USER']};'
        f'PWD={environ['DB_PASSWORD']};'
        f'TrustServerCertificate=yes;'
    )

    return conn


if __name__ == '__main__':
    conn = get_db_connection()
    cur = conn.cursor()
    schema_text = load_schema_file()
    cur.execute('SELECT @@VERSION')
    print(cur.fetchone())

    commands = schema_text.split(';')
    conn.autocommit = True
    for command in commands:
        print(command)
        cur.execute(command)

    # print(cur.fetchone())
    cur.close()
    conn.close()
