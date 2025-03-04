import google.generativeai as genai
import json
from typing import Tuple, Dict
from fuzzywuzzy import process
from dotenv import load_dotenv
import os
from .player_names import PLAYER_NAME_MAPPING, DB_PLAYER_NAMES
# Load environment variables from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_response(prompt: str, as_json: bool = False) -> str:
    """Fetch response from Gemini API."""
    # Note: "gemini-2.0-flash-lite-preview-02-05" is a placeholder; use a valid model
    model = genai.GenerativeModel("gemini-2.0-flash-lite-preview-02-05")  # Adjust to a supported model
    config = {"response_mime_type": "application/json"} if as_json else {}
    try:
        response = model.generate_content(prompt, generation_config=config)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return '{"query": "SELECT 0 as fallback", "params": {}}' if as_json else "API error occurred"

def fuzzy_match_player_name(user_input: str, threshold: int = 75) -> str:
    """Find the closest matching player name with fallback."""
    user_input_lower = user_input.lower()
    if user_input_lower in PLAYER_NAME_MAPPING:
        return PLAYER_NAME_MAPPING[user_input_lower]
    match, score = process.extractOne(user_input, DB_PLAYER_NAMES)
    if score >= threshold:
        return match
    return f"%{user_input}%"

def extract_player_name(question: str) -> str:
    """Extract potential player name with comprehensive exclusion."""
    words = question.lower().split()
    exclude = {
        "how", "many", "runs", "did", "score", "in", "which", "match", "wickets", 
        "against", "highest", "strike", "rate", "ipl", "final", "playoffs", 
        "player", "took", "most", "single", "of", "taken", "who", "by", "what",
        "where", "when", "vs", "and", "or", "the", "a", "an", "at", "on", "has",
        "scored", "take", "was", "is", "were", "100", "200", "50", "this", "that"
    }
    potential_names = [w for w in words if w not in exclude and not w.isdigit()]
    return " ".join(potential_names[:3]) if potential_names else "unknown"

def generate_query(question: str) -> Tuple[str, Dict[str, str], str]:
    """Convert an IPL question into an SQL query and parameters."""
    user_player_input = extract_player_name(question)
    db_player_name = fuzzy_match_player_name(user_player_input) if user_player_input != "unknown" else None
    use_like = db_player_name and "%" in db_player_name

    prompt = f"""
You are an expert IPL cricket SQL query generator. Convert the given question into a JSON object with keys "query" (SQL with :name placeholders) and "params" (a dictionary). Handle all IPL questions—simple, complex, comparative, and deep—with match-specific details where needed.

### Database Schema ###
- Tables:
  - matches: id, season (TEXT), city, date, match_type, player_of_match, venue, team1, team2, toss_winner, toss_decision, winner, result, result_margin, target_runs, target_overs, super_over, method, umpire1, umpire2
  - balls: match_id, inning, batting_team, bowling_team, over, ball, batter, bowler, non_striker, batsman_runs, extra_runs, total_runs, extras_type, is_wicket, player_dismissed, dismissal_kind, fielder
- Relationship: balls.match_id = matches.id

### Key Rules ###
- For runs, use 'batsman_runs'.
- For wickets, count rows where 'is_wicket = 1'.
- Player names use 'Initial(s) LastName' (e.g., 'V Kohli'); if wildcards (e.g., '%Zaheer%'), use LIKE and limit to 1 if ambiguous.
- Team names are full (e.g., 'Mumbai Indians'); abbreviations like 'CSK' are invalid—use 'Chennai Super Kings'.
- Seasons are TEXT (e.g., '2016', '2007/08'); always pass as strings in params (e.g., '2016').
- For match-specific queries (e.g., "in which match"), group by match_id and include all non-aggregated columns (e.g., 'm.date') in GROUP BY or use aggregates.
- For highest stats in a match, group by match_id, order DESC, and return all tied top results with match details.
- 'final match' or 'IPL final' means match_type = 'Final'.
- Join tables only when season, venue, or match details are needed.
- Default to total stats if intent is unclear.

### Examples ###
1. "How many wickets did Zaheer take?"
   {{ "query": "SELECT COUNT(*) as wickets FROM balls WHERE bowler = :bowler AND is_wicket = 1", "params": {{"bowler": "Z Khan"}} }}
2. "How many runs did MS Dhoni score in 2016?"
   {{ "query": "SELECT SUM(b.batsman_runs) as runs FROM balls b JOIN matches m ON b.match_id = m.id WHERE b.batter = :batter AND m.season = :season", "params": {{"batter": "MS Dhoni", "season": "2016"}} }}
3. "In which match did Virat Kohli score 100?"
   {{ "query": "SELECT m.team1, m.team2, m.season, m.date FROM balls b JOIN matches m ON b.match_id = m.id WHERE b.batter = :batter GROUP BY m.id, m.team1, m.team2, m.season, m.date HAVING SUM(b.batsman_runs) >= 100 ORDER BY m.date LIMIT 1", "params": {{"batter": "V Kohli"}} }}
4. "Which player took the most wickets in a single match of IPL?"
   {{ "query": "WITH WicketsPerMatch AS (SELECT b.bowler, b.match_id, m.team1, m.team2, m.season, COUNT(*) as wickets FROM balls b JOIN matches m ON b.match_id = m.id WHERE b.is_wicket = 1 GROUP BY b.bowler, b.match_id, m.team1, m.team2, m.season), MaxWickets AS (SELECT MAX(wickets) as max_wickets FROM WicketsPerMatch) SELECT w.bowler, w.team1, w.team2, w.season, w.wickets FROM WicketsPerMatch w JOIN MaxWickets mw ON w.wickets = mw.max_wickets", "params": {{}} }}

### Question ###
{question}

### Preprocessed Player Name ###
{'Player name to use: ' + db_player_name if db_player_name else 'No player specified'}

Respond with ONLY the JSON object. If unsure, default to a safe total stat query (e.g., total runs or wickets).
"""
    response = get_gemini_response(prompt, as_json=True)
    print(f"Raw Gemini response: {response}")
    try:
        data = json.loads(response)
        query = data.get("query", "SELECT 0 as fallback")
        params = data.get("params", {})
        if "season" in params:
            params["season"] = str(params["season"])
        if "SELECT" not in query.upper():
            return "SELECT 0 as fallback", {}, "Invalid query generated"
        return query, params, None
    except json.JSONDecodeError:
        print("JSON parsing failed")
        return "SELECT 0 as fallback", {}, "Error parsing Gemini response"

def format_answer(question: str, result: str) -> str:
    """Format query result into a detailed natural language answer."""
    prompt = f"""
You are an IPL cricket expert. Format the SQL result into a detailed, natural language answer with match context where applicable.

### Rules ###
- If result is '0', say 'no runs scored', 'no wickets taken', etc., with context (e.g., 'in that scenario').
- For match-specific queries (e.g., 'team1:CSK,team2:RCB,season:2016'), say "Player scored X runs in CSK vs RCB, 2016."
- For highest stats with ties (e.g., 'bowler1:team1:team2:season:wickets,bowler2:...'), list all: "Player1 took X wickets in Team1 vs Team2, Year; Player2 took X wickets in Team3 vs Team4, Year."
- For comparisons (e.g., 'V Kohli:973,RG Sharma:800'), say "X scored more runs than Y, with X_runs to Y_runs."
- For single totals (e.g., '119'), say "Player took X wickets in their IPL career."
- Handle malformed results gracefully.

### Question and Result ###
Question: {question}
Result: {result}

Return a natural language answer (plain text only).
"""
    return get_gemini_response(prompt)