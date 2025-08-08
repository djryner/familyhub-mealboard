import os
os.environ.setdefault("REPL_ID", "devcontainer")
print("Starting main.py")  # Add this line
from app import app
import routes  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
