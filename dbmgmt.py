import sqlite3
import random

def connection():
    conn = sqlite3.connect("TourOdishaAI/locinfo.db")
    return conn

def db_init():
    conn = sqlite3.connect("TourOdishaAI/locinfo.db")
    c = conn.cursor()

    # Full user account system will be integrated soon.

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            email TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            description TEXT,
            best_time TEXT,
            tips TEXT,
            user_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            ratings REAL DEFAULT 0.0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        ) 
    ''')

    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS photos (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         submission_id INTEGER,
    #         photo_path TEXT,
    #         FOREIGN KEY(submission_id) REFERENCES submission(id)
    #     )
    # ''')
    # Coming soon!

    c.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER,
            rated_by TEXT,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            FOREIGN KEY(submission_id) REFERENCES submissions(id),
            FOREIGN KEY(rated_by) REFERENCES users(id),
            UNIQUE(submission_id, rated_by)
        )
    ''')

    conn.commit()

def create_user(username, email=None):
    with connection() as conn:
        userid = random.randint(1000000000000, 999999999999999)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", (userid, username, email))
        conn.commit()

        cursor.execute("SELECT id FROM users WHERE name=?", (username, ))
        userid = cursor.fetchone()
        return userid[0] #Returns userid for user to view after creating acc

def get_user_id(username):
    with connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE name=?", (username, ))
        userid = c.fetchone()
        return userid if userid else None
    
def addSubmission(location, description, best_time, tips, username):
    userid = get_user_id(username)
    print(userid[0])
    if not userid:
        raise ValueError("User not found. Please create your user profile before proceeding further.")
    else:
        with connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO submissions (location, description, best_time, tips, user_id) VALUES (?, ?, ?, ?, ?)", (location, description, best_time, tips, userid[0]))

def list_submissions():
    with connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT s.id, s.location, s.description, s.best_time, s.tips, u.name,
                IFNULL(ROUND(AVG(r.rating), 2), 'unrated') as avg_rating
            FROM submissions s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN ratings r ON s.id = r.submission_id
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """)
        rows = c.fetchall()
        return rows
    
def add_rating(submission_id, username, rating):
    with connection() as conn:
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5.")
        user_id = get_user_id(username)[0]
        if not user_id:
            raise ValueError("User not found. Create the user first.")
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO ratings (submission_id, rated_by, rating)
            VALUES (?, ?, ?)
        """, (submission_id, user_id, rating))
        conn.commit()

db_init()
