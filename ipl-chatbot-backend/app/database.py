from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError  

DATABASE_URL = "postgresql://postgres:123@localhost:5432/ipl_db"
engine = create_engine(DATABASE_URL)

def execute_query(query: str, params: dict = None) -> list:

    if params is None:
        params = {}
    try:
        with engine.connect() as conn:
            print(f"Database - Executing query: {query}, Params: {params}, Type: {type(params)}")
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            print(f"Query result: {rows}")
            return rows
    except OperationalError as e:
        raise RuntimeError(f"Database connection failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {str(e)}")