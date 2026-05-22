# database/setup_db.py
import sqlite3
import os

# Get the absolute path to ensure it always saves in the correct folder
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "jarvis.db")

def init_db():
    print(f"Initializing database at: {DB_PATH}")
    
    # Connecting creates the file if it doesn't exist
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the Tasks (Tarefas) table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        status TEXT DEFAULT 'pendente',
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create the Schedule (Agenda) table since it's also a required tool
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        data_hora DATETIME NOT NULL,
        tipo TEXT NOT NULL,
        descricao TEXT
    )
    ''')

    # Save changes and close
    conn.commit()
    conn.close()
    print("Tables 'tarefas' and 'agenda' created successfully.")

if __name__ == "__main__":
    init_db()