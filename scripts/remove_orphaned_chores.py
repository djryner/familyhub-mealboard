import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""
Script to find and optionally delete orphaned ChoreOccurrence rows (chores) whose task_id does not exist in chore_metadata.
"""
from app import app
from db import db
from models import ChoreOccurrence, ChoreMetadata


def find_orphaned_occurrences():
    orphans = ChoreOccurrence.query.filter(~ChoreOccurrence.task_id.in_(db.session.query(ChoreMetadata.task_id))).all()
    return orphans

def main():
    with app.app_context():
        orphans = find_orphaned_occurrences()
        if not orphans:
            print("No orphaned ChoreOccurrence rows found.")
            return
        print(f"Found {len(orphans)} orphaned ChoreOccurrence rows:")
        for occ in orphans:
            print(f"  id={occ.id} task_id={occ.task_id} due_date={occ.due_date}")
        # Uncomment below to delete them:
        # for occ in orphans:
        #     db.session.delete(occ)
        # db.session.commit()
        print("(No changes made. Uncomment code to delete.)")

if __name__ == "__main__":
    main()
