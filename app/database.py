import sqlite3
import bcrypt
from uuid import uuid4
from app import app
from app import login_manager
from datetime import datetime, timedelta
from flask_login import UserMixin

DATABASE = app.config['DATABASE']

class User(UserMixin):
    def __init__(self, user_id, user_email, user_nickname, user_verified_email):
        self.id = user_id
        self.user_id = user_id
        self.email = user_email
        self.nickname = user_nickname
        self.verified_email = user_verified_email

@login_manager.user_loader
def load_user(user_id):
    """Return a User object or None"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id, user_email, "
            "user_nickname, user_verified_email "
            "FROM users "
            "WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        if row == None:
            return None
        return User(*row)
        #return User(row[0], row[1], row[2], row[3])


def hash_password(password):
    """Hashes an utf-8 string and returns an utf-8 string of the hash"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def create_user(email, password):
    """Creates a new user"""
    with sqlite3.connect(DATABASE) as conn:
        pw_hash = hash_password(password)
        conn.execute("INSERT INTO users (user_email, user_hash) VALUES (?, ?)", (email, pw_hash))
        conn.commit()

def check_password(email, password):
    """Return True upon success, False upon failure"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_hash FROM users WHERE user_email = ?;", (email,))
        user_hash = cursor.fetchone()
        if user_hash == None:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user_hash[0].encode('utf-8'))

def get_user_id(email):
    """Return the user_id for a given email"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id FROM users WHERE user_email = ?;", (email,))
        user_id = cursor.fetchone()[0]
        return user_id

def is_valid_user_id(user_id):
    """Returns True if the user_id exists, False if not"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id FROM users WHERE user_id = ?;", (user_id,))    
        return cursor.fetchone()[0] != None

def get_user(user_id):
    """Return a user based on a user_id"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id, user_email, "
            "user_nickname, user_verified_email "
            "FROM users "
            "WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        user_id, user_email, user_nickname, user_verified_email = row
        user = {
            "user_id":user_id,
            "user_email": user_email,
            "user_nickname": user_nickname,
            "user_verified_email": user_verified_email
        }
        return user

def save_nickname(user_id, user_nickname):
    """Save the user nickname"""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("UPDATE users SET user_nickname = ? "
            "WHERE user_id = ?", (user_nickname, user_id))
        conn.commit()

def generate_verification_link(user_id):
    code = str(uuid4())
    dt_today = datetime.now()
    dt_delta = timedelta(days=2)
    dt_future = dt_today + dt_delta
    str_future = dt_future.isoformat()

    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT INTO activations "
            "(act_code, act_user_id, act_expiration) "
            "VALUES (?, ?, ?)", (code, user_id, str_future))
        conn.commit()

def verify_user_email(activation_code):
    """Return True on success, False on failure"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT act_user_id, act_expiration FROM activations WHERE act_code = ?", (activation_code,))
        user_id, act_expiration = cursor.fetchone()
        if user_id == None:
            return False
        # TODO check expiration date
        cursor.execute("UPDATE users SET user_verified_email = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        print("USER email is verified!")
        return True


# Create the database tables in case that they do not exist yet.
db_schema_script = """
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "activations" (
	"act_id"	INTEGER,
	"act_code"	TEXT NOT NULL,
	"act_user_id"	INTEGER NOT NULL,
	"act_expiration"	TEXT NOT NULL,
	PRIMARY KEY("act_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER,
	"user_email"	TEXT UNIQUE,
	"user_hash"	TEXT,
	"user_nickname"	TEXT UNIQUE,
	"user_verified_email"	INTEGER DEFAULT 0,
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
