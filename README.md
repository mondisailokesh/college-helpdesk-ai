# College Helpdesk AI

A local college helpdesk chatbot built with Python and Streamlit.

## Project Overview

This project provides a small AI-driven helpdesk for college students. It supports:

- student login via `database/users.db`
- complaint ticket creation, listing, and deletion
- password update support via `tools/password_reset.py`
- local knowledge retrieval from `knowledge/*.md`
- RAG-style answers when knowledge is available
- a simple Streamlit UI in `frontend/app.py`

## Repository Structure

- `frontend/app.py` - Streamlit application UI and chat flow
- `router.py` - main query router and intent logic
- `intents/classifier.py` - rule-based intent detection
- `rag/` - retrieval and LLM integration helpers
- `tools/` - utility modules for auth, tickets, contact, and password reset
- `knowledge/` - markdown files containing college knowledge
- `database/` - SQLite database initializer scripts and DB files
- `college_db/` - local ChromaDB database storage for retrieval (optional)
- `evaluation/` - evaluation scripts and test cases
- `test_*.py` - unit tests for key behavior

## Setup

1. Create a local Python virtual environment and activate it. For example:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run frontend/app.py
```

> Note: `venv/` is intentionally ignored by Git via `.gitignore`, so your local virtual environment remains private and is not pushed to GitHub.

## Usage

- Log in with student credentials from `database/users.db`
- Ask questions like:
  - `What is the hostel fee?`
  - `show my tickets`
  - `i want to reset my password`
  - `mess food is not well to eat`
- For password updates, provide the new password with your student ID if requested.

## Notes

- The app is designed to operate without a remote LLM by using local markdown knowledge fallback.
- Password changes are applied directly to the SQLite `database/users.db` for this prototype.
- Temporary generated files (`__pycache__`) have been removed for a clean workspace.

## Recommended Cleanup

If you want to keep the repo clean, do not commit generated artifacts such as `__pycache__` directories.
