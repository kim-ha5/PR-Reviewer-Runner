from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/run")
def run_command():
    command = request.args.get("cmd")
    subprocess.run(command, shell=True)
    return "Command executed"