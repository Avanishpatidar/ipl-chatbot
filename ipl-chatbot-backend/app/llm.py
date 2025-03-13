import google.generativeai as genai
import json
from typing import Tuple, Dict, Optional
from fuzzywuzzy import process
from dotenv import load_dotenv
from .player_names import PLAYER_NAME_MAPPING, DB_PLAYER_NAMES, TEAM_NAME_MAPPING
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
 
genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel("gemini-2.0-flash-lite-preview-02-05")

def get_gemini_response(prompt: str, as_json: bool = False) -> str:
    """Fetch response from Gemini API with error handling."""
    config = {"response_mime_type": "application/json"} if as_json else {}
    try:
        response = MODEL.generate_content(prompt, generation_config=config)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return '{"query": "SELECT 0 as fallback", "params": {}}' if as_json else "API error occurred"

def fuzzy_match_player_name(user_input: str, threshold: int = 75) -> str:
    """
    Match user-provided player name to database name with improved fuzzy logic.
    Prioritizes popular players and handles ambiguous cases better.
    """
    # Dictionary of popular players that should be prioritized in matching
    POPULAR_PLAYERS = {
        "kohli": "V Kohli",
        "virat": "V Kohli",
        "virat kohli": "V Kohli",
        "Virat Kohli ": "V Kohli",
        "rohit": "RG Sharma",  # Specify the exact Rohit Sharma we want
        "rohit sharma": "RG Sharma",
        "sharma": "RG Sharma",
        "dhoni": "MS Dhoni",
        "ms dhoni": "MS Dhoni",
        "bumrah": "JJ Bumrah",
        "jasprit": "JJ Bumrah",
        "jasprit bumrah": "JJ Bumrah",
        "jadeja": "RA Jadeja",
        "ravindra": "RA Jadeja",
        "ravindra jadeja": "RA Jadeja",
        "gayle": "CH Gayle",
        "chris": "CH Gayle",
        "chris gayle": "CH Gayle",
        "russell": "AD Russell",
        "andre": "AD Russell",
        "andre russell": "AD Russell",
        "warner": "DA Warner",
        "david": "DA Warner",
        "david warner": "DA Warner",
        "maxwell": "GJ Maxwell",
        "glenn": "GJ Maxwell",
        "glenn maxwell": "GJ Maxwell",
        "hardik": "HH Pandya",
        "pandya": "HH Pandya",
        "hardik pandya": "HH Pandya",
        "raina": "SK Raina",
        "suresh": "SK Raina",
        "suresh raina": "SK Raina",
        "bhuvneshwar": "B Kumar",
        "bhuvi": "B Kumar",
        "kumar": "B Kumar",
        "abd": "AB de Villiers",
        "devilliers": "AB de Villiers",
        "ab de villiers": "AB de Villiers",
        "villiers": "AB de Villiers",
        "pant": "RR Pant",
        "rishabh": "RR Pant",
        "rishabh pant": "RR Pant"
    }
    
    user_input_lower = user_input.lower()
    
    # First check if it's a direct match in our predefined mapping
    if user_input_lower in PLAYER_NAME_MAPPING:
        return PLAYER_NAME_MAPPING[user_input_lower]
    
    # Check if it's a popular player that should be prioritized
    if user_input_lower in POPULAR_PLAYERS:
        return POPULAR_PLAYERS[user_input_lower]
    
    # If no direct match, use fuzzy matching
    matches = process.extract(user_input, DB_PLAYER_NAMES, limit=3)
    
    # If we have confident matches
    if matches and matches[0][1] >= threshold:
        # If the top match is very confident (over 90%), use it
        if matches[0][1] >= 90:
            return matches[0][0]
        
        # If we have multiple matches with similar scores (within 5%), prioritize well-known players
        if len(matches) > 1 and (matches[0][1] - matches[1][1] <= 5):
            # Define recognition patterns for well-known players
            popular_patterns = [
                ("V Kohli", ["kohli", "virat"]),
                ("RG Sharma", ["rohit", "sharma"]),
                ("MS Dhoni", ["dhoni", "ms"]),
                ("JJ Bumrah", ["bumrah", "jasprit"]),
                ("AB de Villiers", ["villiers", "abd"]),
                ("CH Gayle", ["gayle", "chris"]),
                ("SK Raina", ["raina", "suresh"]),
                ("RA Jadeja", ["jadeja", "ravindra"]),
                # Add more popular players as needed
            ]
            
            # Check if any of our matches is a popular player
            for player, keywords in popular_patterns:
                for match, score in matches:
                    if match == player or any(keyword in user_input_lower for keyword in keywords):
                        return player
        
        # If no special case was triggered, return the top match
        return matches[0][0]
    
    # If confidence is low, use a LIKE query with the original input
    return f"%{user_input}%"


def extract_player_name(question: str) -> str:
    """Extract potential player name with comprehensive exclusion."""
    words = question.lower().split()
    exclude = {
        "how", "many", "runs", "did", "score","scored" , "in", "which", "match", "wickets",
        "against", "highest", "strike", "rate", "ipl", "final", "playoffs",
        "player", "took", "most", "single", "of", "taken", "who", "by", "what",
        "where", "when", "vs", "and", "or", "the", "a", "an", "at", "on", "has",
        "scored", "take", "was", "is", "were", "100", "200", "50", "this", "that",
        "times", "time", "stadium", "last", "overs", "batting", "pairs", "run",
        "three", "seasons", "history", "bowling", "type", "out", "digit",
        "slowest", "opening", "partnership", "lasted", "balls", "fifty", "plus",
        "scores", "total", "lose", "game", "aggregate", "minimum", "batsmen",
        "innings", "hit", "longest", "six", "dismissal", "lbw", "head", "to",
        "records", "titles", "individuals", "boundaries", "wankhede", "eden",
        "gardens", "best", "figure", "m", "chidambaram", "2nd", "loss", "chased",
        "succesful", "chase", "all", "captain", "90s", "first", "ball", "4", "6"
    }
    potential_names = [w for w in words if w not in exclude and not w.isdigit()]
    return " ".join(potential_names[:3]) if potential_names else "unknown"

def preprocess_question(question: str) -> str:
    """Replace team abbreviations with full names and correct common typos."""
    words = question.lower().split()
    processed_words = [TEAM_NAME_MAPPING.get(word, word) for word in words]
    typo_corrections = {"worng": "wrong", "asnwer": "answer"}
    processed_words = [typo_corrections.get(word, word) for word in processed_words]
    return " ".join(processed_words)

def generate_query(question: str) -> Tuple[str, Dict[str, str], str]:
    """Convert an IPL question into an SQL query and parameters using the improved prompt."""
    preprocessed_question = preprocess_question(question)
    user_player_input = extract_player_name(preprocessed_question)
    db_player_name = fuzzy_match_player_name(user_player_input) if user_player_input != "unknown" else None
    use_like = db_player_name and "%" in db_player_name

    prompt = f"""
You are an expert IPL cricket SQL query generator. Your task is to convert the given question into a JSON object with two keys: "query" (SQL statement using :name placeholders) and "params" (a dictionary of parameters). The system must handle all types of IPL questions—simple (e.g., total runs), complex (e.g., highest chase under specific conditions), comparative (e.g., team head-to-head records), deep (e.g., slowest fifties), and edge cases (e.g., tied matches, incomplete seasons)—including match-specific details when required. Be robust to typos, unclear English, or vague intent by relying on preprocessed input and sensible defaults.

### Database Schema ###
- Tables:
  - matches: id (INTEGER), season (TEXT, e.g., '2016' or '2007/08'), city (TEXT), date (TEXT), match_type (TEXT, e.g., 'League', 'Final'), player_of_match (TEXT), venue (TEXT), team1 (TEXT), team2 (TEXT), toss_winner (TEXT), toss_decision (TEXT, 'bat' or 'field'), winner (TEXT, NULL if tie/no result), result (TEXT, e.g., 'runs', 'wickets', 'tie'), result_margin (INTEGER), target_runs (INTEGER), target_overs (REAL), super_over (TEXT, 'Y' or 'N'), method (TEXT, e.g., 'D/L', NULL if normal), umpire1 (TEXT), umpire2 (TEXT)
  - balls: match_id (INTEGER), inning (INTEGER, 1 or 2, 3+ for super overs), batting_team (TEXT), bowling_team (TEXT), over (INTEGER, 1-20), ball (INTEGER, 1-6+ for extras), batter (TEXT), bowler (TEXT), non_striker (TEXT), batsman_runs (INTEGER), extra_runs (INTEGER), total_runs (INTEGER), extras_type (TEXT, e.g., 'wides', 'noballs', NULL if none), is_wicket (INTEGER, 0 or 1), player_dismissed (TEXT, NULL if no wicket), dismissal_kind (TEXT, e.g., 'caught', 'run out', NULL if no wicket), fielder (TEXT, NULL if not applicable)
- Relationship: balls.match_id = matches.id

### Key Rules ###
- Runs:
  - Use batsman_runs for batsman-specific runs (excludes extras).
  - Use total_runs for team or match totals (includes extras).
  - For successful chases, use SUM(total_runs) where inning = 2 and m.winner = b.batting_team.
- Wickets:
  - For bowlers: Count is_wicket = 1 where dismissal_kind NOT IN ('run out', 'retired hurt', 'obstructing the field').
  - For total wickets: Count all is_wicket = 1.
  - Exclude super overs (inning <= 2) unless specified.
- Player Names:
  - Format: 'Initial(s) LastName' (e.g., 'V Kohli', 'MS Dhoni').
  - If ambiguous, use LIKE (e.g., LIKE '%Kohli%') and LIMIT 1, preferring recent seasons (ORDER BY m.season DESC).
- Team Names:
  - Use full names (e.g., 'Mumbai Indians'). Pre-mapped abbreviations (e.g., 'CSK' → 'Chennai Super Kings').
- Seasons:
  - Stored as TEXT (e.g., '2016', '2007/08'). Pass as strings in params. Use LIKE for partial matches (e.g., '2007%').
- Overs:
  - 'Power play': Overs 1-6 (over <= 6).
  - 'Middle overs': Overs 7-15 (over BETWEEN 7 AND 15).
  - 'Death overs': Overs 16-20 (over >= 16).
  - Exclude wides (extras_type != 'wides') for balls faced/bowled unless specified.
- Match Types:
  - 'Final': match_type = 'Final'.
  - 'Playoffs': match_type IN ('Qualifier 1', 'Qualifier 2', 'Eliminator', 'Final').
  - 'League': match_type = 'League'.
- Match-Specific Queries:
  - Group by match_id and include all non-aggregated columns in GROUP BY or use aggregates.
  - For ties/no-results, check winner IS NULL or result = 'tie'.
- Highest/Lowest Stats:
  - Group by relevant fields, order by the stat (DESC/ASC), and LIMIT 1.
  - Include contextual fields (e.g., team1, team2, season, venue).
- Joins:
  - Join matches and balls only when necessary. Avoid for total stats if possible.
- Rates and Averages:
  - Strike Rate (batsman): (SUM(batsman_runs) * 100.0 / COUNT(CASE WHEN extras_type != 'wides' THEN 1 END)).
  - Run Rate (team): (SUM(total_runs) * 6.0 / SUM(CASE WHEN extras_type NOT IN ('wides', 'noballs') THEN 1 ELSE 0 END)).
  - Economy Rate (bowler): (SUM(total_runs) * 6.0 / SUM(CASE WHEN extras_type NOT IN ('wides', 'noballs') THEN 1 ELSE 0 END)).
  - Average (batsman): SUM(batsman_runs) / COUNT(CASE WHEN is_wicket = 1 THEN 1 END).
  - Average (bowler): SUM(total_runs) / COUNT(CASE WHEN is_wicket = 1 AND dismissal_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 END).
- Edge Cases:
  - Super overs: Filter inning > 2 if requested; otherwise, exclude (inning <= 2).
  - D/L method: Filter method = 'D/L' if specified.
  - Incomplete matches: Handle winner IS NULL or result_margin IS NULL.
- Default Behavior:
  - If unclear, default to total stats (e.g., total runs, total wins) across all seasons.
  - Assume 'all-time' unless season/team/opponent is specified.
- Unanswerable Questions:
  - For unanswerable queries (e.g., 'longest six'), use a fallback (e.g., most sixes) and add "note" in params.

### Examples ###
1. "How many matches between Mumbai Indians and Chennai Super Kings in 2019?"
   {{ "query": "SELECT COUNT(*) as matches FROM matches m WHERE m.season = :season AND ((m.team1 = :team1 AND m.team2 = :team2) OR (m.team1 = :team2 AND m.team2 = :team1))", "params": {{"season": "2019", "team1": "Mumbai Indians", "team2": "Chennai Super Kings"}} }}
2. "Total runs by V Kohli in power play in 2016?"
   {{ "query": "SELECT SUM(b.batsman_runs) as runs FROM balls b JOIN matches m ON b.match_id = m.id WHERE b.batter = :batter AND b.over <= 6 AND m.season = :season", "params": {{"batter": "V Kohli", "season": "2016"}} }}
3. "Highest team score in an IPL final?"
   {{ "query": "SELECT b.batting_team, SUM(b.total_runs) as total_runs, m.team1, m.team2, m.season, m.venue FROM balls b JOIN matches m ON b.match_id = m.id WHERE m.match_type = 'Final' AND b.inning <= 2 GROUP BY b.batting_team, m.id, m.team1, m.team2, m.season, m.venue ORDER BY total_runs DESC LIMIT 1", "params": {{}} }}
4. "Most wickets by a bowler in death overs in playoffs?"
   {{ "query": "SELECT b.bowler, COUNT(*) as wickets, m.id, m.team1, m.team2, m.season FROM balls b JOIN matches m ON b.match_id = m.id WHERE b.is_wicket = 1 AND b.over >= 16 AND b.dismissal_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') AND m.match_type IN ('Qualifier 1', 'Qualifier 2', 'Eliminator', 'Final') GROUP BY b.bowler, m.id, m.team1, m.team2, m.season ORDER BY wickets DESC LIMIT 1", "params": {{}} }}
5. "What is the economy rate of JJ Bumrah?"
   {{ "query": "SELECT (SUM(b.total_runs) * 6.0 / SUM(CASE WHEN b.extras_type NOT IN ('wides', 'noballs') THEN 1 ELSE 0 END)) as economy_rate FROM balls b WHERE b.bowler = :bowler AND b.inning <= 2", "params": {{"bowler": "JJ Bumrah"}} }}
6. "Slowest fifty in IPL (most balls faced)?"
   {{ "query": "SELECT b.batter, SUM(b.batsman_runs) as runs, COUNT(CASE WHEN b.extras_type != 'wides' THEN 1 END) as balls, m.team1, m.team2, m.season FROM balls b JOIN matches m ON b.match_id = m.id WHERE b.inning <= 2 GROUP BY b.batter, m.id, m.team1, m.team2, m.season HAVING SUM(b.batsman_runs) >= 50 ORDER BY balls DESC LIMIT 1", "params": {{}} }}
7. "Highest runs chased by Royal Challengers Bangalore in 2018?"
   {{ "query": "SELECT m.id, m.team1, m.team2, m.season, SUM(b.total_runs) as chased_runs FROM balls b JOIN matches m ON b.match_id = m.id WHERE b.inning = 2 AND m.winner = :team AND m.season = :season GROUP BY m.id, m.team1, m.team2, m.season ORDER BY chased_runs DESC LIMIT 1", "params": {{"team": "Royal Challengers Bangalore", "season": "2018"}} }}
8. "Most catches by a fielder in a single match?"
   {{ "query": "SELECT b.fielder, COUNT(*) as catches, m.id, m.team1, m.team2, m.season FROM balls b JOIN matches m ON b.match_id = m.id WHERE b.dismissal_kind = 'caught' AND b.fielder IS NOT NULL GROUP BY b.fielder, m.id, m.team1, m.team2, m.season ORDER BY catches DESC LIMIT 1", "params": {{}} }}
9. "Team with most ties in IPL history?"
   {{ "query": "SELECT team, COUNT(*) as ties FROM (SELECT m.team1 as team FROM matches m WHERE m.result = 'tie' UNION ALL SELECT m.team2 as team FROM matches m WHERE m.result = 'tie') GROUP BY team ORDER BY ties DESC LIMIT 1", "params": {{}} }}
10. "Longest six in IPL history?"
    {{ "query": "SELECT b.batter, COUNT(*) as sixes FROM balls b WHERE b.batsman_runs = 6 GROUP BY b.batter ORDER BY sixes DESC LIMIT 1", "params": {{"note": "Distance data not available; showing batsman with most sixes instead."}} }}

### Question ###
{preprocessed_question}

### Preprocessed Player Name ###
{'Player name to use: ' + db_player_name if db_player_name else 'No player specified'}

Respond with ONLY the JSON object. If unsure, default to a safe total stat query (e.g., total runs or wickets). For unanswerable questions (e.g., 'longest six' without distance data), use a fallback query and note in params.
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
    """Format query result into a detailed natural language answer with enhanced clarity."""
    prompt = f"""
You are an IPL cricket expert tasked with transforming SQL query results into detailed, natural language answers that are clear, engaging, and informative. Provide context, insights, and explanations based on the original question and the result, making the answer suitable for cricket enthusiasts.

### Rules ###
- **Single Values**: For totals (e.g., 'runs: 500'), state "X scored 500 runs in [context, e.g., their IPL career, 2016 season]." Include season, teams, or venue if specified in the result.
- **Zero or Null Results**: Explain meaningfully, e.g., "No runs were scored by X in [context]" or "No matches met the criteria."
- **Match-Specific Context**: If result includes match details (e.g., 'team1:CSK, team2:RCB, season:2016, runs:150'), say "In the match between CSK and RCB in 2016, [entity] scored 150 runs." Add venue if available.
- **Highest/Lowest Stats**: For records (e.g., 'batter: V Kohli, runs: 200, team1:MI, team2:CSK, season:2016'), say "V Kohli scored the highest 200 runs in a match between MI and CSK in 2016." List ties if present (e.g., "Both X and Y scored 200 runs...").
- **Comparisons**: For multiple entities (e.g., 'CSK: 5 wins, RCB: 3 wins'), say "CSK outperformed RCB with 5 wins to 3 wins in their head-to-head record."
- **Rates and Averages**: Format appropriately:
  - Strike Rate: "X had a strike rate of 150.50 in [context]."
  - Economy Rate: "X's economy rate was 7.25 in [context]."
  - Average: "X averaged 45.30 in [context]."
- **Lists or Aggregates**: For grouped data (e.g., 'venue1: 2 matches, venue2: 1 match'), say "2 matches were played at venue1, and 1 at venue2."
- **Unanswerable or Fallback**: If result includes a note (e.g., 'note: Distance data not available'), reflect it: "The longest six distance isn’t tracked, but X hit the most sixes with Y."
- **Malformed Results**: If result is invalid (e.g., empty string, unexpected format), return "Sorry, I couldn’t process the result for this question. Please try again."

### Question and Result ###
Question: {question}
Result: {result}

Return a natural language answer (plain text only). Keep it concise yet detailed, avoiding repetition unless adding value.
"""
    return get_gemini_response(prompt)



