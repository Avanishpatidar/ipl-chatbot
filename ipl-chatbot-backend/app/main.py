from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import Question
from .database import execute_query
from .llm import generate_query, format_answer
from dotenv import load_dotenv
import os
import json

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

app = FastAPI(title="IPL Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

season_mapping = {
    "2008": "2007/08", "2009": "2009", "2010": "2009/10", "2011": "2011",
    "2012": "2012", "2013": "2013", "2014": "2014", "2015": "2015",
    "2016": "2016", "2017": "2017", "2018": "2018", "2019": "2019",
    "2020": "2020/21", "2021": "2021", "2022": "2022", "2023": "2023",
    "2024": "2024",
}

@app.post("/ask")
async def ask_question(question: Question):
    try:
        query, params, error_message = generate_query(question.text)
        print(f"Main - Query: {query}, Params: {params}, Type: {type(params)}")
        
        if error_message:
            return {"answer": error_message}
        
        if "season" in params:
            user_year = params["season"]
            params["season"] = season_mapping.get(user_year, user_year)
            print(f"Mapped season: {params['season']}")
        
        result = execute_query(query, params)
        if result is None or not result:  # Handle None or empty result
            result_value = "0"
        elif len(result[0]) > 1:  # Multi-row result
            result_value = ",".join(f"{row[0]}:{':'.join(str(x) for x in row[1:])}" for row in result)
        else:
            result_value = str(result[0][0] if result[0][0] is not None else "0")
        print(f"Result value: {result_value}")
        
        answer = format_answer(question.text, result_value)
        return {"answer": answer}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"answer": "Sorry, an unexpected error occurred. Please try again."}