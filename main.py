#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, flash, redirect
from flask_socketio import SocketIO, emit

import logging
from logging import Formatter, FileHandler

from models import db
from models import Achat, Personne, Remboursement

from forms import AchatForm, DeleteForm

from sqlalchemy import extract
from sqlalchemy.sql import functions

from datetime import datetime

import os
import json

import recipe_scraper

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    return app

app = create_app()
socketio = SocketIO(app)


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

    previous_repayment = Remboursement.query.order_by(Remboursement.date.desc()).first()
    print(previous_repayment.id)

    total = Achat.query.with_entities(functions.sum(Achat.montant)).filter(Achat.date > previous_repayment.date).scalar()
    if not total:
        total = 0

    personnes = Personne.query.all()
    nb_personnes = len(personnes)
    data = []
    for personne in personnes:
        achats = Achat.query.filter(Achat.date > previous_repayment.date).filter_by(auteur = personne).all()
        total_personne = Achat.query.with_entities(functions.sum(Achat.montant)).filter(Achat.date >= previous_repayment.date).filter_by(auteur = personne).scalar()
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
        achat = Achat(montant=form.montant.data,
                      message=form.message.data,
                      auteur=form.personne.data)
        db.session.add(achat)
        db.session.commit()
        flash('Achat effectué avec succès')
        return redirect("achats", code=303)
    return render_template('pages/add.html', form=form)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    form = DeleteForm(request.form)
    if request.method == 'POST' and form.validate():
        print("reture")
        db.session.delete(form.achat.data)
        db.session.commit()
        flash('Achat retiré avec succès')
        return redirect("achats", code=303)
    return render_template('pages/delete.html', form=form)


#----------------------------------------------------------------------------#
# Recettes
#----------------------------------------------------------------------------#

@app.route('/recettes')
def recettes():
    return render_template('pages/recettes.html')

@socketio.on('my event')
def handle_connect(data):
    print('received data: ' + str(data))

@socketio.on('get recipes')
def handle_recipes(data):
    recettes = recipe_scraper.get_recipes(data['data'], max_recipes=8)
    print("recettes: ", data['data'])
    emit('recipes result', json.dumps([overview.toJSON() for overview in recettes]))

@socketio.on('get recipe')
def handle_recipes(data):
    recipe = recipe_scraper.get_recipe(identifier=data['ident'])
    emit('recipe result', json.dumps(recipe.toJSON()))

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    socketio.run(app)
