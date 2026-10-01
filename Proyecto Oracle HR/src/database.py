import oracledb
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus


def get_connection_string():
    user = "HR"
    password = "HR"
    host = "localhost"
    port = 1521
    service_name = "XEPDB1"
    return user, password, host, port, service_name

def get_engine():
    user, password, host, port, service_name = get_connection_string()
    conn_str = (
        f"oracle+oracledb://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/?service_name={service_name}"
    )
    return create_engine(conn_str, pool_pre_ping=True)

def run_query(query: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df