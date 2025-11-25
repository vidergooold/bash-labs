from flask import Flask, jsonify
import socket
import sys

app = Flask(__name__)

HOSTNAME = socket.gethostname()
PORT = int(sys.argv[1])

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "instance": HOSTNAME,
        "port": PORT
    })

@app.route("/process")
def process():
    return jsonify({
        "message": "Processed by instance",
        "instance": HOSTNAME,
        "port": PORT
    })

if __name__ == "__main__":
    print(f"Running instance on port {PORT}")
    app.run(port=PORT)
