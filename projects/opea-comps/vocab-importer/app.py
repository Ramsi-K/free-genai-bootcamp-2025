from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return {"message": "Hello from Korean Vocabulary Importer"}


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    # Make sure to use host='0.0.0.0' to bind to all interfaces
    app.run(host="0.0.0.0", port=8000, debug=True)
