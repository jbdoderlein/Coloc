#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, flash

import logging
from logging import Formatter, FileHandler

from models import db
from models import Achat, Personne

from forms import AchatForm

from sqlalchemy import extract
from sqlalchemy.sql import functions

from datetime import datetime

import os

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    return app

app = create_app()


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/index.html')


@app.route('/achats')
def achats():
    #TODO: Envoyer la structure:
    # Personne:
    # - liste des achats du mois en cours
    # - total des montants
    # - delta
    # - Total de toutes les dépenses

    total = Achat.query.with_entities(functions.sum(Achat.montant)).filter(extract('month', Achat.date)==datetime.utcnow().month and
                                                             extract('year', Achat.date)==datetime.utcnow().year
                                                             ).scalar()
    if not total:
        total = 0

    personnes = Personne.query.all()
    nb_personnes = len(personnes)
    data = []
    for personne in personnes:
        achats = Achat.query.filter(extract('month', Achat.date)==datetime.utcnow().month and
                                    extract('year', Achat.date)==datetime.utcnow().year
                                    ).filter_by(auteur = personne).all()
        total_personne = Achat.query.with_entities(functions.sum(Achat.montant)).filter(extract('month', Achat.date)==datetime.utcnow().month and
                                    extract('year', Achat.date)==datetime.utcnow().year
                                    ).filter_by(auteur = personne).scalar()
        if not total_personne:
            total_personne = 0
        data.append({"personne": personne,
                     "achats": achats,
                     "total": total_personne,
                     "delta": total_personne - (total/nb_personnes)
                     })

    return render_template('pages/achats.html', data=data, total=total)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AchatForm(request.form)
    if request.method == 'POST' and form.validate():
        achat = Achat(montant=form.montant.data, message=form.message.data, auteur=form.personne.data)
        db.session.add(achat)
        db.session.commit()
        flash('Achat effectué avec succès')
    return render_template('pages/add.html', form=form)

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
