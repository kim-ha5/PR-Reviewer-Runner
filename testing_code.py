# Sample vulnerable code for testing

from flask import Flask, request
import sqlite3
import subprocess
import hashlib
import pickle

app = Flask(__name__)


@app.route("/run")
def run_command():
    command = request.args.get("cmd")

    # Vulnerability: command injection
    subprocess.run(command, shell=True)

    return "Command executed"


@app.route("/user")
def get_user():
    username = request.args.get("username")

    connection = sqlite3.connect("users.db")

    # Vulnerability: SQL injection
    query = "SELECT * FROM users WHERE username = '" + username + "'"

    result = connection.execute(query)

    return str(result.fetchall())


@app.route("/hash")
def weak_hash():
    password = request.args.get("password")

    # Vulnerability: weak cryptographic hash
    hashed = hashlib.md5(password.encode()).hexdigest()

    return hashed