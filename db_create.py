from config import SQLALCHEMY_DATABASE_URI

from app import db
import os.path

# Creates all the tables and the database.
db.create_all()

