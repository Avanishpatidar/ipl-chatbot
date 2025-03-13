from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import Question
from .database import execute_query
from .llm import generate_query, format_answer
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

app = FastAPI(title="IPL Chatbot", description="A chatbot for detailed IPL stats")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SEASON_MAPPING = {
    "2008": "2007/08", "2009": "2009", "2010": "2009/10", "2011": "2011",
    "2012": "2012", "2013": "2013", "2014": "2014", "2015": "2015",
    "2016": "2016", "2017": "2017", "2018": "2018", "2019": "2019",
    "2020": "2020/21", "2021": "2021", "2022": "2022", "2023": "2023",
    "2024": "2024",
}

@app.post("/ask", response_model=dict)
async def ask_question(question: Question):
    """Handle user question and return a natural language answer."""
    try:
        query, params, error_message = generate_query(question.text)
        if error_message:
            raise HTTPException(status_code=400, detail=error_message)

        if "season" in params:
            params["season"] = SEASON_MAPPING.get(params["season"], params["season"])

        result = execute_query(query, params)
        result_value = (
            "0" if not result else
            ",".join(f"{row[0]}:{':'.join(str(x) for x in row[1:])}" for row in result)
            if len(result[0]) > 1 else str(result[0][0] or "0")
        )
        answer = format_answer(question.text, result_value)
        return {"answer": answer}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

