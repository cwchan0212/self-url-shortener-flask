from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from url_shortener import app
from .models import db

app.config.from_prefixed_env()
print(f" # {app.config['SQLALCHEMY_DATABASE_URI']} #2")

try:
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()
        print("Tables created successfully")

except Exception as e:
    print("An error occurred while creating the tables:", e)

exit()
