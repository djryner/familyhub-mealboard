"""
Script to find and optionally remove or fix local chores with fake (UUID) task_ids that do not exist in Google Tasks.
"""
import re

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from models import ChoreMetadata, db

def is_fake_uuid(task_id):
    return bool(re.fullmatch(r"[0-9a-fA-F\-]{36}", task_id))

def find_fake_task_ids():
    return ChoreMetadata.query.filter(ChoreMetadata.task_id.op('regexp')(r'^[0-9a-fA-F\-]{36}$')).all()

def main():
    with app.app_context():
        fake_chores = find_fake_task_ids()
        if not fake_chores:
            print("No fake UUID task_ids found.")
            return
        print(f"Found {len(fake_chores)} fake UUID task_ids:")
        for meta in fake_chores:
            print(f"  {meta.task_id} | {meta.title}")
        # Uncomment below to delete them:
        for meta in fake_chores:
             db.session.delete(meta)
        db.session.commit()
        print("(No changes made. Uncomment code to delete.)")

if __name__ == "__main__":
    main()
