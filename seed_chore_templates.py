"""Seeds the database with a default set of chore templates.

This script is idempotent, meaning it can be run multiple times without creating
duplicate entries. It checks for existing chore templates by name and category
before inserting new ones.
"""

from app import app  # provides app context
from db import db  # << use the shared SQLAlchemy instance
from models import ChoreTemplate

# A list of (chore_name, category) tuples to be seeded into the database.
SEED = [
    ("Make your bed", "Bedroom"),
    ("Pick up toys", "Bedroom"),
    ("Put away clothes", "Bedroom"),
    ("Dust shelves", "Bedroom"),
    ("Change bed sheets", "Bedroom"),
    ("Sweep the floor", "Cleaning"),
    ("Mop the floor", "Cleaning"),
    ("Vacuum carpets", "Cleaning"),
    ("Wipe down tables", "Cleaning"),
    ("Clean mirrors", "Cleaning"),
    ("Empty the trash", "Cleaning"),
    ("Wash dishes", "Kitchen"),
    ("Dry and put away dishes", "Kitchen"),
    ("Wipe kitchen counters", "Kitchen"),
    ("Sweep the kitchen floor", "Kitchen"),
    ("Load the dishwasher", "Kitchen"),
    ("Unload the dishwasher", "Kitchen"),
    ("Help set the table", "Kitchen"),
    ("Clear the table", "Kitchen"),
    ("Clean out the fridge", "Kitchen"),
    ("Fold laundry", "Laundry"),
    ("Sort laundry by color", "Laundry"),
    ("Put away clean clothes", "Laundry"),
    ("Start a load of laundry", "Laundry"),
    ("Hang clothes to dry", "Laundry"),
    ("Feed the dog", "Pet Care"),
    ("Give the dog fresh water", "Pet Care"),
    ("Brush the dog", "Pet Care"),
    ("Clean the dog's food bowl", "Pet Care"),
    ("Walk the dog", "Pet Care"),
    ("Water plants", "Outdoor"),
    ("Pull weeds", "Outdoor"),
    ("Sweep the porch", "Outdoor"),
    ("Help rake leaves", "Outdoor"),
    ("Pick up sticks in the yard", "Outdoor"),
    ("Carry in groceries", "Household"),
    ("Organize shoes", "Household"),
    ("Wipe door handles", "Household"),
    ("Help sort mail", "Household"),
    ("Restock toilet paper", "Household"),
    ("Take out recycling", "Household"),
    ("Help wash the car", "Outdoor"),
    ("Shake out rugs", "Cleaning"),
    ("Disinfect light switches", "Cleaning"),
    ("Straighten bookshelves", "Bedroom"),
    ("Organize school backpack", "School Prep"),
    ("Pack lunch", "School Prep"),
    ("Help make breakfast", "Kitchen"),
    ("Help make dinner", "Kitchen"),
    ("Pick up dog waste in yard", "Pet Care"),
]


def run():
    """Seeds the database with chore templates from the SEED list."""
    with app.app_context():
        # Ensure that the database tables are created before seeding.
        db.create_all()

        # Fetch existing chore templates to avoid creating duplicates.
        existing = {(t.name, t.category) for t in ChoreTemplate.query.all()}
        # Determine which templates from the SEED list are new.
        to_add = [
            ChoreTemplate(name=n, category=c)
            for (n, c) in SEED
            if (n, c) not in existing
        ]

        if to_add:
            # If there are new templates, add them to the database in a single bulk operation.
            db.session.bulk_save_objects(to_add)
            db.session.commit()
            print(f"Seeded {len(to_add)} chore templates (added only missing).")
        else:
            # If no new templates are found, report that the database is up to date.
            count = ChoreTemplate.query.count()
            print(f"Chore templates already up to date ({count} rows).")


if __name__ == "__main__":
    run()
