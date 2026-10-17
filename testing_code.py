#Sample vulnerable code for testing

# from flask import Flask, request
# import subprocess

# app = Flask(__name__)

# @app.route("/run")
# def run_command():
#     command = request.args.get("cmd")
#     subprocess.run(command, shell=True)
#     return "Command executed"


from flask import Flask, request
import sqlite3
import subprocess
import hashlib
import pickle

app = Flask(__name__)


# Vulnerability 1: Command injection
@app.route("/run")
def run_command():
    command = request.args.get("cmd")
    subprocess.run(command, shell=True)
    return "Command executed"


# Vulnerability 2: SQL injection
@app.route("/user")
def get_user():
    user_id = request.args.get("id")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
    return str(cursor.fetchall())


# Vulnerability 3: Insecure deserialization
@app.route("/load")
def load_data():
    data = request.data
    result = pickle.loads(data)
    return str(result)


# Vulnerability 4: Weak hashing algorithm
@app.route("/hash")
def hash_password():
    password = request.args.get("password", "")
    hashed = hashlib.md5(password.encode()).hexdigest()
    return hashed


if __name__ == "__main__":
    app.run(debug=True)
