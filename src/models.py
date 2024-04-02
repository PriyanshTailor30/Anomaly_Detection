# your_app/models.py

from flask import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"
