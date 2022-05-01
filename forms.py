from wtforms import Form, StringField, FloatField, validators
from wtforms_sqlalchemy.fields import QuerySelectField
from models import Personne

class AchatForm(Form):
    personne = QuerySelectField("Personne", query_factory=lambda:Personne.query, get_label="name")
    message = StringField('Message', [validators.Length(min=3, max=100)])
    montant = FloatField("Montant")
