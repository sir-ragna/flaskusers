import sqlite3
import bcrypt
from app import app

DATABASE = app.config['DATABASE']

def hash_password(password):
    """Hashes an utf-8 string and returns an utf-8 string of the hash"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def create_user(username, password):
    """Creates a new user"""
    with sqlite3.connect(DATABASE) as conn:
        pw_hash = hash_password(password)
        conn.execute("INSERT INTO users (user_name, user_hash) VALUES (?, ?)", (username, pw_hash))
        conn.commit()

def check_password(username, password):
    """Return True upon success, False upon failure"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id, user_name, user_hash FROM users WHERE user_name = ?;", (username,))
        user_id, user_name, user_hash = cursor.fetchone()
        return bcrypt.checkpw(password.encode('utf-8'), user_hash.encode('utf-8'))

def get_user_id(username):
    """Return the user_id for a given username"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id FROM users WHERE user_name = ?;", (username,))
        user_id = cursor.fetchone()[0]
        return user_id

def is_valid_user_id(user_id):
    """Returns True if the user_id exists, False if not"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id FROM users WHERE user_id = ?;", (user_id,))    
        return cursor.fetchone()[0] != None

# Create the database tables in case that they do not exist yet.
db_schema_script = """
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER,
	"user_name"	TEXT UNIQUE,
	"user_hash"	TEXT,
	PRIMARY KEY("user_id" AUTOINCREMENT)
);
COMMIT;
"""
with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.executescript(db_schema_script)
    conn.commit()
    print("Executed DB schema script")
    cursor.close()
