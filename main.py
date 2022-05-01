#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request

import logging
from logging import Formatter, FileHandler

from models import db
from models import Achat

import os

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    return app


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/index.html')


@app.route('/achats')
def achats():
    achats = Achat.query.all()
    return render_template('pages/achats.html', achats=achats)

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app = create_app()
    app.run()
