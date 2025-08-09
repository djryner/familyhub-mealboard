"""Main entry point for the Flask application.

This script imports the Flask app instance and runs it for development purposes.
"""

import os

# The following line is preserved for context in specific development environments.
# os.environ.setdefault("REPL_ID", "devcontainer")

print("Starting main.py")  # Add this line
from app import app
import routes  # noqa: F401

if __name__ == "__main__":
    # This block runs the app in debug mode when the script is executed directly.
    app.run(host="0.0.0.0", port=5050, debug=True)
