# Project Database

## Dependencies
- Flask>=2.2
- Flask-SQLAlchemy>=3.0
- SQLAlchemy>=1.4

## Notes
- This project uses SQLite via the built-in Python `sqlite3` module.

## Quick setup (recommended from project root)

1. Create a virtual environment and activate it:

    **Windows**

    Create:
    ```bash
    python -m venv venv
    ```

    Activate:
    ```bash
    venv\Scripts\activate
    ```

    **Linux / macOS**

    Create:
    ```bash
    python3 -m venv venv
    ```

    Activate:
    ```bash
    source venv/bin/activate
    ```

2. Install dependencies:

    ```bash
    pip install -r Database/requirements.txt
    ```

3. Initialize the database (creates tables if they don't exist):

    ```bash
    python Database/init_db.py
    ```

4. Populate the databse (Adds some basic examples):

    ```bash
    python Database/populate_db.py
    ```