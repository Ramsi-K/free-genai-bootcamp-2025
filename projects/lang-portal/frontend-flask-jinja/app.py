from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# Ensure the necessary directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)  # Ensure images folder exists

# Ensure required HTML templates exist
html_templates = {
    "index.html": """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>HagXwon</title>
        <link rel='stylesheet' href='/static/css/style.css'>
        <script src='/static/js/theme-toggle.js' defer></script>
        <link rel='icon' href='/static/images/favicon.ico' type='image/x-icon'>
    </head>
    <body>
        <div class='container'>
            <nav class='navbar'>
                <h1>HagXwon</h1>
                <button id='theme-toggle'>🌞/🌙</button>
            </nav>
            <div class='content'>
                <h2>Welcome to HagXwon</h2>
                <p>Your personalized language learning experience.</p>
            </div>
        </div>
    </body>
    </html>
    """
}

for filename, content in html_templates.items():
    filepath = os.path.join("templates", filename)
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write(content)

# Ensure required CSS and JS files exist
css_content = """
body {
    font-family: Arial, sans-serif;
    background-color: white;
    color: black;
    text-align: center;
    transition: background 0.3s, color 0.3s;
}
.dark-mode {
    background-color: #1e1e1e !important;
    color: white !important;
}
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    background: #4A90E2;
    color: white;
}
button {
    padding: 10px;
    cursor: pointer;
    border: none;
    background-color: #357ABD;
    color: white;
    font-size: 16px;
    border-radius: 5px;
}
button:hover {
    background-color: #255a9b;
}
.content {
    padding: 50px;
}
"""

js_content = """
console.log('Theme toggle script loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) {
        console.error('Theme toggle button not found!');
        return;
    }
    
    console.log('Checking local storage for theme:', localStorage.getItem('theme'));
    
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        console.log('Dark mode activated from storage');
    }
    
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
        console.log('Toggled theme, new mode:', localStorage.getItem('theme'));
    });
});
"""

with open("static/css/style.css", "w") as f:
    f.write(css_content)

with open("static/js/theme-toggle.js", "w") as f:
    f.write(js_content)

# Ensure a default favicon exists
favicon_path = "static/images/favicon.ico"
if not os.path.exists(favicon_path):
    with open(favicon_path, "wb") as f:
        f.write(b"")  # Create an empty file as a placeholder


# Serve static files explicitly
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)


# Serve favicon explicitly
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        "static/images", "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


# Routes
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return "<h1>Dashboard</h1>"


@app.route("/word-practice")
def word_practice():
    return "<h1>Word Practice</h1>"


@app.route("/listening-app")
def listening_app():
    return "<h1>Listening App</h1>"


@app.route("/sentence-practice")
def sentence_practice():
    return "<h1>Sentence Practice</h1>"


if __name__ == "__main__":
    try:
        # Adjusting Flask to work in a sandboxed environment
        app.run(
            host="127.0.0.1",
            port=8080,
            debug=False,
            threaded=False,
            use_reloader=False,
        )
    except Exception as e:
        print(f"Error starting Flask app: {e}")
