import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:123@localhost:5432/ipl_db"

def init_db():
    engine = create_engine(DATABASE_URL)
    
    matches_df = pd.read_csv("matches.csv")
    matches_df.to_sql("matches", engine, if_exists="replace", index=False)
    
    balls_df = pd.read_csv("balls.csv")
    balls_df.to_sql("balls", engine, if_exists="replace", index=False)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()