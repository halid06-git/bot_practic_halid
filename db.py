import sqlite3
from datetime import datetime

conn = sqlite3.connect('mood.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS days (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        mood INTEGER,
        work REAL,
        sleep REAL,
        comment TEXT
    )
''')
conn.commit()

def save(user_id, mood, work, sleep, comment):
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('DELETE FROM days WHERE user_id=? AND date=?', (user_id, today))
    c.execute('INSERT INTO days VALUES (NULL,?,?,?,?,?,?)', (user_id, today, mood, work, sleep, comment))
    conn.commit()

def get_last7(user_id):
    c.execute('SELECT mood, work, sleep FROM days WHERE user_id=? ORDER BY date DESC LIMIT 7', (user_id,))
    return c.fetchall()

def get_history(user_id):
    c.execute('SELECT date, mood, work, sleep, comment FROM days WHERE user_id=? ORDER BY date DESC LIMIT 10', (user_id,))
    return c.fetchall()

def clear(user_id):
    c.execute('DELETE FROM days WHERE user_id=?', (user_id,))
    conn.commit()

def get_insight(user_id):
    c.execute('SELECT AVG(mood) FROM days WHERE user_id=? AND sleep>7', (user_id,))
    good = c.fetchone()[0]
    c.execute('SELECT AVG(mood) FROM days WHERE user_id=? AND sleep<=7', (user_id,))
    bad = c.fetchone()[0]
    return good, bad