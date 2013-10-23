import sqlite3
import hashlib

DB = None
CONN = None

def connect_to_db():
    global DB, CONN
    CONN = sqlite3.connect("thewall.db")
    DB = CONN.cursor()

def authenticate(username, password):
    query = """SELECT id FROM Users WHERE username = ? AND password = ?"""
    DB.execute(query, (username, SHA1_hash(password)))
    row = DB.fetchone()
    
    return row

def get_user_by_name(username):
    query = """SELECT id FROM Users WHERE username = ?"""
    DB.execute(query, (username,))
    row = DB.fetchone()
    if row:
        return row[0]
    return row

def get_name_by_id(user_id):
    query = """SELECT username FROM Users WHERE id = ?"""
    DB.execute(query, (user_id,))
    row = DB.fetchone()
    return row[0]

def get_posts_by_user_id(user_id):
    query = """SELECT owner_id, author_id, created_at, content FROM Wall_Posts WHERE owner_id = ? ORDER BY id DESC"""
    DB.execute(query, (user_id,))
    rows = DB.fetchall()
    return rows #this is a list

def write_wall_post(owner_id, author_id, post_text):
    query = """INSERT into Wall_Posts (owner_id, author_id, created_at, content) values (?, ?, datetime('now'), ?) """
    DB.execute(query, (owner_id, author_id, post_text))
    CONN.commit()

def create_user(username, password):
    query = """INSERT into Users (username, password) values (?, ?) """
    DB.execute(query, (username, SHA1_hash(password)))
    CONN.commit()

def get_newsfeed():
    query = """SELECT owner_id, author_id, created_at, content FROM wall_posts ORDER BY id DESC LIMIT 5"""
    DB.execute(query)
    rows = DB.fetchall()
    return rows

def SHA1_hash(hash_this):
    # python's hash() hashes differently on 32- and 64-bit machines, LOL
    return hashlib.sha1(hash_this).hexdigest()

connect_to_db()