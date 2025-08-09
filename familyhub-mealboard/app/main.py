"""Main Flask application for the FamilyHub Mealboard.

This app provides a simple API to fetch meals and serves the main dashboard page.
"""

from flask import Flask, jsonify, render_template
from app.api.calendar import get_meals

# Note: template_folder and static_folder are relative to the app's root directory
app = Flask(__name__, template_folder="../../templates", static_folder="../../static")


@app.get("/api/meals")
def meals():
    """API endpoint to get the list of meals."""
    return jsonify(get_meals())


@app.get("/")
def index():
    """Serves the main index page for the meal board."""
    return render_template("index.html")
