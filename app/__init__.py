#ISC License (ISC)

#Copyright 2020 Fabio Mariani (fabio.mariani555@gmail.com), DH.ARC, University of Bologna

#Permission to use, copy, modify, and/or distribute this software for
#any purpose with or without fee is hereby granted, provided that the
#above copyright notice and this permission notice appear in all copies.

#THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
#OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.



#init file of "app" package, the Hub
from flask import Flask
from flask_login import LoginManager
from SPARQLWrapper import SPARQLWrapper, JSON
from apscheduler.schedulers.background import BackgroundScheduler
import os

#instance_relative_config   safety trick to  hide sensible information path
app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')


scheduler = BackgroundScheduler(timezone="europe/rome")
scheduler.start()

#triplestore
ts = SPARQLWrapper(app.config['TS_URL'])
ts.setReturnFormat(JSON)

#admin login
login = LoginManager(app)

if not os.path.exists(os.path.dirname("dump/")):
        os.makedirs(os.path.dirname("dump/"))
if not os.path.exists(os.path.dirname("temp/")):
        os.makedirs(os.path.dirname("temp/"))


#at bottom, prevent circular import
from app import routes