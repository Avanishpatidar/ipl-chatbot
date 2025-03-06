# IPL Chatbot

An AI-powered chatbot for IPL (Indian Premier League) that provides insights, statistics, and more.

## Backend Setup

### Prerequisites
- Python 3.x
- PostgreSQL
- pip (Python package installer)
- Gemini API Key ([Get it here](https://ai.google.dev))

### Installation & Configuration

#### Clone the Repository
```bash
git clone https://github.com/Avanishpatidar/ipl-chatbot.git
cd ipl-chatbot/ipl-chatbot-backend
```

#### Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: `venv\Scripts\activate`
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
Create or update the `.env` file:
```plaintext
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/ipl_db
```
Replace `user`, `password`, and `your_gemini_api_key_here` with your actual credentials.

#### Set Up the Database
Ensure PostgreSQL is running, then initialize the database schema and load IPL data:
```bash
# Create tables
python3 scripts/init.db.py

# Load seed data (if required)
python3 scripts/init.py  # Optional: Only if initial data needs to be populated
```

#### Run the Backend Server
```bash
uvicorn main:app --reload
```
The backend will start at [http://localhost:8000](http://localhost:8000).

---

## Frontend Setup

### Prerequisites
- Node.js
- npm

### Installation & Execution

#### Navigate to the Frontend Directory
```bash
cd ../ipl-chatbot-frontend
```

#### Install Dependencies
```bash
npm install
```

#### Start the Frontend Server
```bash
npm run dev
```

Access the frontend at [http://localhost:3000](http://localhost:3000).

---

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

