from flask import Flask, request

app = Flask(__name__)

@app.route("/download")
def download_file():
    filename = request.args.get("file")
    file_path = "/var/www/uploads/" + filename

    with open(file_path, "r") as file:
        return file.read()