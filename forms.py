from wtforms import Form, StringField, FloatField, validators
from wtforms_sqlalchemy.fields import QuerySelectField
from models import Personne, Achat

class AchatForm(Form):
    personne = QuerySelectField("Personne", query_factory=lambda:Personne.query, get_label="name")
    message = StringField('Message', [validators.Length(min=3, max=100)])
    montant = FloatField("Montant")

class DeleteForm(Form):
    achat = QuerySelectField("Achat", query_factory=lambda:Achat.query, get_label="message")
