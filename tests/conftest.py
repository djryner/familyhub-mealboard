"""Pytest configuration file.

This file sets up the test environment by ensuring that the project's root
directory is included in the Python path. This allows test modules to import
application modules (e.g., from `services`, `models`) correctly.
"""

import sys
from pathlib import Path

# Add the project root directory to the Python path to resolve imports
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
