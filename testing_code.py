#Sample vulnerable code for testing


from flask import Flask, request
import sqlite3
import subprocess
import hashlib
import pickle

app = Flask(__name__)

@app.route("/run")
def run_command():
    command = request.args.get("cmd")
    subprocess.run(command, shell=True)
    return "Command executed"
