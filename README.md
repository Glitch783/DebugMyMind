# ?? Coding Misconception Detector

> **IEEE TechForGood Internship Project 2026**

An AI-powered tool that automatically analyzes beginner Python student code submissions, identifies common coding misconceptions, and generates personalized explanations and micro-exercises to help students learn — all in real time.

---

## ? Features

- **?? Static Analysis** — AST-based parser detects code anti-patterns with high certainty
- **? Safe Code Execution** — Sandboxed runtime using `RestrictedPython` to capture errors and tracebacks
- **?? Semantic Matching** — Sentence-transformer embeddings (`all-MiniLM-L6-v2`) match student code to a curated misconception taxonomy
- **?? LLM Explanations** — OpenRouter API (GPT-4o-mini by default) generates friendly, personalized explanations and micro-exercises
- **?? Student Portal** — Students submit code and receive instant feedback
- **?? Instructor Dashboard** — Instructors view class-wide analytics, top misconceptions, and per-student summaries
- **??? Persistent Storage** — SQLite database stores all submissions and student profiles

---

## ??? Architecture

```
misconception-detector/
+-- app/                        # FastAPI backend
¦   +-- main.py                 # API routes & startup logic
¦   +-- models.py               # SQLAlchemy database models
¦   +-- database.py             # DB engine & session setup
¦   +-- pipeline/               # Analysis pipeline
¦       +-- analyser.py         # Pipeline orchestrator
¦       +-- ast_parser.py       # Static AST analysis
¦       +-- executor.py         # Sandboxed code execution
¦       +-- embedder.py         # Semantic similarity matching
¦       +-- llm_analyser.py     # LLM explanation generation
+-- frontend/                   # Streamlit UI
¦   +-- home.py                 # Main app entrypoint
¦   +-- student_view.py         # Student submission portal
¦   +-- instructor_view.py      # Instructor analytics dashboard
¦   +-- components.py           # Reusable UI components & CSS
+-- data/
¦   +-- misconception_taxonomy.json   # Curated misconception definitions
¦   +-- sample_submissions.json       # Seed data for demo
+-- requirements.txt
+-- run.sh                      # Linux/macOS startup script
+-- run.ps1                     # Windows (PowerShell) startup script
+-- .env                        # Environment configuration
```

### Analysis Pipeline

```
Student Code
     ¦
     +--? [1] AST Parser        ? Detects static anti-patterns (high certainty, conf: 0.95)
     ¦
     +--? [2] Safe Executor     ? Runs code in sandbox, captures errors & tracebacks
     ¦
     +--? [3] Embedder          ? Cosine similarity vs. taxonomy (all-MiniLM-L6-v2)
     ¦         +-- Taxonomy JSON (misconceptions, keywords, bad/fix code examples)
     ¦
     +--? [4] LLM Analyser     ? Generates explanation + micro-exercise (via OpenRouter)
               +-- Fallback template if API key is unset
```

---

## ?? Quick Start

### Prerequisites

- Python 3.10+
- An [OpenRouter](https://openrouter.ai/) API key *(optional — works without it using fallback templates)*

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/misconception-detector.git
cd misconception-detector
```

### 2. Create and Activate a Virtual Environment

```bash
# Linux / macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit the `.env` file with your values:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | `your_key_here` | OpenRouter API key for LLM explanations |
| `DATABASE_URL` | `sqlite:///./misconceptions.db` | SQLAlchemy database connection string |
| `MODEL_NAME` | `openai/gpt-4o-mini` | LLM model to use via OpenRouter |
| `MAX_TOKENS` | `600` | Max tokens for LLM response |

> **Note:** If `OPENROUTER_API_KEY` is not set, the system will automatically fall back to template-based explanations — no API key is required to run the app.

### 5. Run the Application

**Linux / macOS:**
```bash
chmod +x run.sh
./run.sh
```

**Windows (PowerShell):**
```powershell
.\run.ps1
```

This starts:
- **FastAPI backend** at `http://localhost:8000`
- **Streamlit frontend** at `http://localhost:8501`

The database is automatically seeded with sample submissions on first run.

---

## ??? Usage

### Student Portal
1. Open `http://localhost:8501` in your browser
2. Enter your **Student ID** and **Name** in the sidebar
3. Navigate to the **Student Portal**
4. Paste your Python code in the editor
5. Click **Analyze My Code** to receive:
   - Identified misconception & confidence score
   - Friendly explanation of the error
   - A targeted micro-exercise to reinforce correct understanding
   - Your submission history

### Instructor Dashboard
1. Select **Instructor Dashboard** in the sidebar navigation
2. View class-wide metrics:
   - Total submissions & unique students
   - Top misconceptions across the class (bar chart)
   - Per-student submission summaries

---

## ?? API Reference

The FastAPI backend exposes the following REST endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/submit` | Submit code for analysis |
| `GET` | `/history/{student_id}` | Get last 10 submissions for a student |
| `GET` | `/analytics` | Misconception counts (all submissions) |
| `GET` | `/top-misconceptions` | Top 5 most frequent misconceptions |
| `GET` | `/students-summary` | All students with submission counts |
| `GET` | `/instructor-metrics` | Class-wide dashboard metrics |

Interactive API docs are available at `http://localhost:8000/docs`.

---

## ?? Misconception Taxonomy

The taxonomy (`data/misconception_taxonomy.json`) is a curated list of common beginner Python misconceptions. Each entry includes:

- `id` — Unique identifier (also used as AST override flag)
- `name` — Human-readable misconception name
- `description` — What the misconception is
- `keywords` — Terms used for semantic matching
- `example_bad_code` — Example of the problematic code pattern
- `example_fix` — Corrected version of the code

---

## ??? Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI + Uvicorn |
| **Frontend UI** | Streamlit |
| **Database** | SQLite via SQLAlchemy |
| **Static Analysis** | Python `ast` module |
| **Sandboxed Execution** | RestrictedPython |
| **Semantic Matching** | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| **LLM Integration** | OpenRouter API (GPT-4o-mini) |
| **Data Validation** | Pydantic v2 |
| **Visualization** | Plotly |

---

## ?? Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## ?? License

This project was developed as part of the **IEEE TechForGood Internship 2026**. See [LICENSE](LICENSE) for details.
