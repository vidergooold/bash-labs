from flask import Flask, jsonify
import socket

app = Flask(__name__)

HOSTNAME = socket.gethostname()

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "instance": HOSTNAME
    })

@app.route("/process")
def process():
    return jsonify({
        "message": "Processed by instance",
        "instance": HOSTNAME
    })

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1])
    print(f"Running instance on port {port}")
    app.run(port=port)
