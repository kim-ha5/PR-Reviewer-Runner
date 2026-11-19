# Sample vulnerable code for testing CodeQL-to-LLM review comments.


# Sample vulnerable code for CodeQL-to-LLM review testing.
# Use only as a static-analysis test fixture.

from flask import Flask, request
import sqlite3
import subprocess
import hashlib
import pickle
from pathlib import Path

app = Flask(__name__)


@app.route("/run")
def run_command():
    command = request.args.get("cmd", "")
    subprocess.run(command, shell=True)
    return "Command executed"


@app.route("/user")
def get_user():
    username = request.args.get("username", "")

    connection = sqlite3.connect(":memory:")
    query = "SELECT * FROM users WHERE username = '" + username + "'"

    result = connection.execute(query)
    return str(result.fetchall())


@app.route("/read")
def read_file():
    filename = request.args.get("filename", "")
    file_path = Path("/tmp/app-files") / filename

    return file_path.read_text()


@app.route("/hash")
def hash_password():
    password = request.args.get("password", "")
    return hashlib.md5(password.encode()).hexdigest()


def load_user_data(serialized_data):
    return pickle.loads(serialized_data)