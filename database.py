import sqlite3

DB_FILE = "workout_records.db"

def init_db():
    conn=sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            exercise TEXT, 
            date TEXT, 
            reps INT, 
            user_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_record(exercise, date, reps, user_id):
    conn=sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO records (exercise, date, reps, user_id)
        VALUES (?, ?, ?, ?)
    ''', (exercise, date, reps, user_id))
    conn.commit()
    conn.close()

def get_records(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
                SELECT exercise, date, reps FROM records WHERE user_id = ?
                   ''', (user_id,))
    rows = cursor.fetchall()  # Fetch all matching rows
    conn.close()
    return rows

