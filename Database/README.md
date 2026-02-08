# Project Database

**Dependencies**
- Flask>=2.2
- Flask-SQLAlchemy>=3.0
- SQLAlchemy>=1.4

**Notes**
- This project uses SQLite via the built-in Python `sqlite3` module.

**Quick setup (recommended from project root)**
1. Create a virtual environment and activate it:

2. Install dependencies:

```
pip install -r Database/requirements.txt
```

3. Initialize the database (creates tables if they don't exist):

```
python Database\init_db.py
```
