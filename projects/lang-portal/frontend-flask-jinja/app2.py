from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# Ensure necessary directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# Create HTML templates
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
    </head>
    <body>
        <nav class='navbar'>
            <h1>HagXwon</h1>
            <button id='theme-toggle'>🌞/🌙</button>
        </nav>
        <div class='container'>
            <h2>Welcome to HagXwon</h2>
            <p>Your personalized language learning experience.</p>
            <ul>
                <li><a href='/dashboard'>Dashboard</a></li>
                <li><a href='/word-practice'>Word Practice</a></li>
                <li><a href='/listening-app'>Listening App</a></li>
                <li><a href='/sentence-practice'>Sentence Practice</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
}

for filename, content in html_templates.items():
    filepath = os.path.join("templates", filename)
    with open(filepath, "w") as f:
        f.write(content)

# Create CSS file
css_content = """
body {
    font-family: Arial, sans-serif;
    background-color: white;
    color: black;
    text-align: center;
    transition: background 0.3s, color 0.3s;
}
.dark-mode {
    background-color: black;
    color: white;
}
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background: linear-gradient(90deg, #4A90E2, #6B2FB3);
    color: white;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}
button {
    padding: 10px;
    border: none;
    cursor: pointer;
    background-color: #357ABD;
    color: white;
    font-size: 16px;
    border-radius: 5px;
    transition: all 0.3s ease;
}
button:hover {
    background-color: #255a9b;
    transform: scale(1.05);
}
"""
with open("static/css/style.css", "w") as f:
    f.write(css_content)

# Create JavaScript file
js_content = """
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) {
        console.error('Theme toggle button not found!');
        return;
    }
    
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
    }
    
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
    });
});
"""
with open("static/js/theme-toggle.js", "w") as f:
    f.write(js_content)


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
    app.run(debug=True)
