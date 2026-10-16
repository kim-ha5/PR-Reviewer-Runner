#Sample vulnerable code for testing

# from flask import Flask, request
# import subprocess

# app = Flask(__name__)

# @app.route("/run")
# def run_command():
#     command = request.args.get("cmd")
#     subprocess.run(command, shell=True)
#     return "Command executed"


import os
import pickle
import sqlite3
import subprocess
import sys


def run_command(user_input):
    # Vulnerability 1: Command injection
    subprocess.run(user_input, shell=True)


def read_file(filename):
    # Vulnerability 2: Path traversal
    with open("/tmp/" + filename, "r") as file:
        return file.read()


def get_user(cursor, username):
    # Vulnerability 3: SQL injection
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()


def load_data(filename):
    # Vulnerability 4: Unsafe deserialization
    with open(filename, "rb") as file:
        return pickle.load(file)


def execute_code(code):
    # Vulnerability 5: Arbitrary code execution
    exec(code)


if __name__ == "__main__":
    # Test command injection
    if len(sys.argv) > 1:
        run_command(sys.argv[1])

    # Test arbitrary code execution
    if len(sys.argv) > 2:
        execute_code(sys.argv[2])
