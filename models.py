from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import column_property

db = SQLAlchemy()

# Set your classes here.

class Personne(db.Model):
    __tablename__ = 'Personne'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)


class Achat(db.Model):
    __tablename__ = 'Achat'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(120), unique=False)
    montant = db.Column(db.Float(120), unique=False)
    date = db.Column(db.DateTime, nullable=False,
                     default=datetime.utcnow)

    auteur_id = db.Column(db.Integer, db.ForeignKey('Personne.id'), nullable=False)
    auteur = db.relationship('Personne', backref=db.backref('achats', lazy=True))

class Remboursement(db.Model):
    __tablename__ = "Remboursement"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
