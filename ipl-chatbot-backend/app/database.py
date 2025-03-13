from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os 

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def execute_query(query: str, params: Optional[Dict] = None) -> List:
    """
    Execute an SQL query on the PostgreSQL database and return results.

    Args:
        query (str): SQL query with named placeholders (e.g., :name).
        params (dict, optional): Parameters to substitute into the query.

    Returns:
        list: List of rows returned by the query.

    Raises:
        RuntimeError: If database connection or query execution fails.
    """
    if params is None:
        params = {}
    try:
        with engine.connect() as conn:
            print(f"Executing query: {query} with params: {params}")
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            print(f"Query result: {rows}")
            return rows
    except OperationalError as e:
        raise RuntimeError(f"Database connection failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e}")


