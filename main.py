# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

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


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    return app


app = create_app()
socketio = SocketIO(app)


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/index.html')


@app.route('/achats/finish')
def finish():
    r1 = Remboursement()
    db.session.add(r1)
    db.session.commit()
    flash('Remboursement effectué avec succès')
    return redirect('/achats')

@app.route('/achats')
def achats():
    previous_repayment = Remboursement.query.order_by(Remboursement.date.desc()).first()
    print(previous_repayment.id)

    total = Achat.query.with_entities(functions.sum(Achat.montant)).filter(
        Achat.date > previous_repayment.date).scalar()
    if not total:
        total = 0

    personnes = Personne.query.all()
    nb_personnes = len(personnes)
    data = []
    begin_date = f"{previous_repayment.date.day}/{previous_repayment.date.month}"
    end_date= f"{datetime.utcnow().day}/{datetime.utcnow().month}"
    for personne in personnes:
        achats = Achat.query.filter(Achat.date > previous_repayment.date).filter_by(auteur=personne).all()
        total_personne = Achat.query.with_entities(functions.sum(Achat.montant)).filter(
            Achat.date >= previous_repayment.date).filter_by(auteur=personne).scalar()
        if not total_personne:
            total_personne = 0
        data.append({"personne": personne,
                     "achats": achats,
                     "total": total_personne,
                     "delta": total_personne - (total / nb_personnes)
                     })

    list_remb = [r.date for r in Remboursement.query.all()]
    list_remb_str = [(id + 1, f"{pre.day}/{pre.month} à {post.day}/{post.month}") for id, pre, post in
                     zip(range(len(list_remb)), list_remb, list_remb[1:] + [datetime.utcnow()])]
    return render_template('pages/achats.html', data=data, total=total, begin_date=begin_date, end_date=end_date, list_remb=list_remb_str)


@app.route('/achats/old/<int:id>')
def achats_old(id: int = 1):
    first_remb = Remboursement.query.get(id)
    second_remb = Remboursement.query.get(id+1)
    if not first_remb:
        return redirect("", code=303)
    else:
        date_from = first_remb.date
        begin_date = f"{first_remb.date.day}/{first_remb.date.month}"
    if not second_remb:
        date_to = datetime.utcnow()
        end_date = f"{datetime.utcnow().day}/{datetime.utcnow().month}"
    else:
        date_to = second_remb.date
        end_date = f"{second_remb.date.day}/{second_remb.date.month}"

    total = Achat.query.with_entities(functions.sum(Achat.montant)).filter(Achat.date > date_from).filter(
        Achat.date < date_to).scalar()
    if not total:
        total = 0

    personnes = Personne.query.all()
    nb_personnes = len(personnes)
    data = []


    for personne in personnes:
        achats = Achat.query.filter(Achat.date > date_from).filter(Achat.date < date_to).filter_by(
            auteur=personne).all()
        total_personne = Achat.query.with_entities(functions.sum(Achat.montant)).filter(Achat.date > date_from).filter(
            Achat.date < date_to).filter_by(auteur=personne).scalar()
        if not total_personne:
            total_personne = 0
        data.append({"personne": personne,
                     "achats": achats,
                     "total": total_personne,
                     "delta": total_personne - (total / nb_personnes)
                     })

    list_remb = [r.date for r in Remboursement.query.all()]
    list_remb_str = [(id+1, f"{pre.day}/{pre.month} à {post.day}/{post.month}") for id, pre, post in
                     zip(range(len(list_remb)), list_remb, list_remb[1:] + [datetime.utcnow()])]


    return render_template('pages/achats.html', data=data, total=total, begin_date=begin_date, end_date=end_date, list_remb=list_remb_str)


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


# ----------------------------------------------------------------------------#
# Recettes
# ----------------------------------------------------------------------------#

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


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    socketio.run(app)
