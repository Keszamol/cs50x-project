import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Users Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

# Daily Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        mood_work INTEGER,
        mood_family INTEGER,
        mood_friends INTEGER,
        mood_selfcare INTEGER,
        gratitude TEXT,
        highlight TEXT
    )
''')

# Todo Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        priority INTEGER,
        titel TEXT,
        description TEXT
    )
''')
conn.commit()
conn.close()
