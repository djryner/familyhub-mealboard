
from flask import Flask, jsonify, render_template
from app.api.calendar import get_meals

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.get("/api/meals")
def meals():
    return jsonify(get_meals())

@app.get("/")
def index():
    return render_template("index.html")
