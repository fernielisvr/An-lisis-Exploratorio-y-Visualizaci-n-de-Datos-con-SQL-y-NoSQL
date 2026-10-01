import pyodbc
import pandas as pd
from sqlalchemy import create_engine

def get_connection_string():
    # Ajusta SERVER según tu instancia local o remota (ej: 'localhost', 'localhost\\SQLEXPRESS')
    server = 'DESKTOP-0A8512L\MSSQLSERVER01'
    database = 'Northwind'
    
    # Para Autenticación de Windows (Trusted_Connection):
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    return conn_str

def get_engine():
    conn_str = get_connection_string()
    # Usa sqlalchemy para interactuar de forma nativa con Pandas
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={conn_str}")
    return engine

def run_query(query: str) -> pd.DataFrame:
    """Ejecuta una consulta SQL y retorna un DataFrame de Pandas."""
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df