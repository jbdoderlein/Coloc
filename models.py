from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from flask_sqlalchemy import SQLAlchemy

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
    message = db.Column(db.String(120), unique=True)
    montant = db.Column(db.String(120), unique=True)
    date = db.Column(db.DateTime, nullable=False,
                     default=datetime.utcnow)

    auteur_id = db.Column(db.Integer, db.ForeignKey('Personne.id'), nullable=False)
    auteur = db.relationship('Personne', backref=db.backref('achats', lazy=True))



