import os
import sqlite3
import pandas as pd


def csv_to_sqlite(csv_path="data/payroll.csv", db_path="data/payroll.db"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_path}")
    
    df = pd.read_csv("data/payroll.csv", dtype={"competency": str})

    connection_to_sqlite = sqlite3.connect(db_path)

    df.to_sql('payroll', connection_to_sqlite, if_exists='replace', index=False)
    connection_to_sqlite.commit()
    connection_to_sqlite.close()

    print(f"Base de dados criada em: {db_path} com {len(df)} registros.")


def query_payroll_data(query, db_path="data/payroll.db"):
    connection_to_sqlite = sqlite3.connect(db_path)
    cursor = connection_to_sqlite.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    result = cursor.fetchall()
    connection_to_sqlite.close()
    return [dict(zip(columns, row)) for row in result]

if __name__ == "__main__":
    csv_to_sqlite()