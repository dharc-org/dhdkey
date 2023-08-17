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
from rdflib import ConjunctiveGraph
import os

#instance_relative_config   safety trick to  hide sensible information path
app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')

#admin login
login = LoginManager(app)
login.init_app(app)


#scheduler = BackgroundScheduler(timezone="europe/rome")
#scheduler.start()

#triplestore
ts = SPARQLWrapper(app.config['TS_URL'])
ts.setReturnFormat(JSON)

graph = ConjunctiveGraph()
graph.parse("dump/dump.nq", format="nquads")
for g in graph.contexts():
        graphstring = g.serialize(format="nt11", encoding="utf-8").decode("utf-8")
        graphname = g.identifier
        query = "INSERT DATA { GRAPH <%s> { %s } }" % (graphname, graphstring)
        ts.setMethod('POST')
        ts.setQuery(query)
        ts.query()


if not os.path.exists(os.path.dirname("dump/")):
        os.makedirs(os.path.dirname("dump/"))
if not os.path.exists(os.path.dirname("temp/")):
        os.makedirs(os.path.dirname("temp/"))



#at bottom, prevent circular import
from app import routes
from app.support import routine_support

#dump everyday at 3 A.M. (italian time zone)
#scheduler.add_job(routine_support.routine, 'cron', hour='3')