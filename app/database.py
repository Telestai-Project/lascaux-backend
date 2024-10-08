import os
from app.models import Base, engine

# Define the path to the database file
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'db/lascaux.db'))

# Ensure the directory for the database exists
db_dir = os.path.dirname(DATABASE_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

def init_db():
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)