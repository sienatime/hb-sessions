import sqlite3

DB = None
CONN = None

def connect_to_db():
    global DB, CONN
    CONN = sqlite3.connect("thewall.db")
    DB = CONN.cursor()

def authenticate(username, password):
    query = """SELECT id FROM Users WHERE username = ? AND password = ?"""
    DB.execute(query, (username, hash(password)))
    row = DB.fetchone()
    
    return row

def get_user_by_name(username):
    query = """SELECT id FROM Users WHERE username = ?"""
    DB.execute(query, (username,))
    row = DB.fetchone()
    return row[0]

def get_posts_by_user_id(user_id):
    query = """SELECT id, owner_id, author_id, created_at, content FROM Wall_Posts WHERE owner_id = ?"""
    DB.execute(query, (user_id,))
    row = DB.fetchall()
    return row #this is a list

connect_to_db()