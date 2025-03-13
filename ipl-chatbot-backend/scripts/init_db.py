import pandas as pd
from sqlalchemy import create_engine
import os


DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    """Initialize the PostgreSQL database with IPL data from CSV files."""
    engine = create_engine(DATABASE_URL)
    matches_df = pd.read_csv("matches.csv")
    balls_df = pd.read_csv("balls.csv")
    
    matches_df.to_sql("matches", engine, if_exists="replace", index=False)
    balls_df.to_sql("balls", engine, if_exists="replace", index=False)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()