import subprocess
import sqlite3

API_KEY = "super-secret-key-123"

def run_command(user_input):
    subprocess.run(user_input, shell=True)

def get_user(username):
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return conn.execute(query).fetchall()