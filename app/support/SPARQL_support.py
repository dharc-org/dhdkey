from app import app, ts
# ISC License (ISC)

# Copyright 2020 Fabio Mariani (fabio.mariani555@gmail.com), DH.ARC, University of Bologna

# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


from rdflib import ConjunctiveGraph, URIRef, Literal, Namespace


#functions to add data
def add_data(graph, quad=False):
    if not quad:
        graphstring = graph.serialize(format="nt11", encoding="utf-8").decode("utf-8")
        query = "INSERT DATA { %s }" % (graphstring)
        post_query(query)
    else:
        for g in graph.contexts():
            graphstring = g.serialize(format="nt11", encoding="utf-8").decode("utf-8")
            graphname = g.identifier
            query = "INSERT DATA { GRAPH <%s> { %s } }" % (graphname, graphstring)
            post_query(query)

def delete_graph(graphid):
    graphname = app.config["BASE_URI"] + "graph/" + graphid
    query = "DROP SILENT GRAPH <%s>" % (graphname)
    post_query(query)

#function to ckeck token validity (es. project already confirmed)
def expired(graphid):
    graphname = app.config["BASE_URI"] + "graph/" + graphid
    query = "ASK WHERE { GRAPH <%s> { ?s ?p ?o } }"% graphname
    ts.setQuery(query)
    result = ts.query().convert().get("boolean")
    return result


def get_all(status):
    query = '''prefix dct:<http://purl.org/dc/terms/>
    prefix doap:<http://usefulinc.com/ns/doap#>
    SELECT distinct ?g ?title ?description ?year ?course ?courseurl ?repository
    (group_concat(distinct ?author;separator="<!=;=!>") as ?authors)
    (group_concat(distinct ?id;separator="<!=;=!>") as ?ids)
    (group_concat(distinct ?hpage;separator="<!=;=!>") as ?homepage)
    WHERE{ 
        GRAPH ?g {
            ?g dct:accessRights '%s'.
            ?pro a foaf:Project;
            dct:title ?title;
            dct:description ?description;
            doap:GitRepository ?repository;
            dct:creator ?aut;
            dct:subject ?courseEntity.
            OPTIONAL {?pro foaf:homepage ?hpage.}
            ?aut foaf:givenName ?name; foaf:familyName ?surname; foaf:mbox ?mail.
            ?courseEntity dct:title ?course; foaf:homepage ?courseurl; dct:coverage ?period.
            ?period rdfs:label ?year.
            
        BIND(CONCAT(STR( ?surname ), ", ", (?name)) as ?author).
        BIND(REPLACE(strbefore( ?mail, "@" ), "\\\\.", "_") as ?id )
        }}group by ?g ?title ?description ?year ?course ?courseurl ?repository'''% status
    data = get_query(query)
    cleaned_data = []

    for elem in data:
        prog_dict = {}
        prog_dict["title"] = elem["title"]["value"]
        prog_dict["graph"] = elem["g"]["value"].replace("https://w3id.org/DHDY/graph/", "")
        prog_dict["description"] = elem["description"]["value"]
        prog_dict["homepage"] = elem["homepage"]["value"]
        prog_dict["repository"] = elem["repository"]["value"]
        prog_dict["year"] = elem["year"]["value"]
        prog_dict["course"] = elem["course"]["value"]
        prog_dict["authors"] = elem["authors"]["value"].split("<!=;=!>")
        prog_dict["ids"] = elem["ids"]["value"].split("<!=;=!>")

        zip_lists = zip(prog_dict["authors"], prog_dict["ids"])
        ordered_ids = sorted(zip_lists)
        prog_dict["ids"] = []
        prog_dict["authors"] = []
        for x, y in ordered_ids:
            prog_dict["ids"].append(y)
            prog_dict["authors"].append(x)

        prog_dict["course"] = elem["course"]["value"]
        prog_dict["courseurl"] = elem["courseurl"]["value"]
        cleaned_data.append(prog_dict)
    return cleaned_data

def by_author(aut_id):
    aut = app.config["BASE_URI"] + "person/" + aut_id
    query = '''prefix dct:<http://purl.org/dc/terms/>
        prefix doap:<http://usefulinc.com/ns/doap#>
        SELECT ?g ?title ?description ?year ?course ?courseurl ?repository ?Autmail ?Firstauthor
        (group_concat(distinct ?author;separator="<!=;=!>") as ?authors) 
        (group_concat(distinct ?id;separator="<!=;=!>") as ?ids)
        (group_concat(distinct ?hpage;separator="<!=;=!>") as ?homepage)
        WHERE{ 
            GRAPH ?g {
                ?g dct:accessRights 'ONLINE'.
                ?pro a foaf:Project;
                dct:title ?title;
                dct:description ?description;
                doap:GitRepository ?repository;
                dct:creator ?aut;
                dct:creator <%s>;
                dct:subject ?courseEntity.
                OPTIONAL {?pro foaf:homepage ?hpage.}
                <%s> foaf:givenName ?Autname; foaf:familyName ?Autsurname; foaf:mbox ?Autmail.
                ?aut foaf:givenName ?name; foaf:familyName ?surname; foaf:mbox ?mail.
                ?courseEntity dct:title ?course; foaf:homepage ?courseurl; dct:coverage ?period.
                ?period rdfs:label ?year.

            BIND(CONCAT(STR( ?surname ), ", ", (?name)) as ?author).
            BIND(CONCAT(STR( ?Autsurname ), ", ", (?Autname)) as ?Firstauthor).
            BIND(REPLACE(strbefore( ?mail, "@" ), "\\\\.", "_") as ?id )
            }}group by ?g ?title ?description ?year ?course ?courseurl ?repository ?Autmail ?Firstauthor''' % (aut, aut)
    data = get_query(query)

    cleaned_data = []

    for elem in data:
        prog_dict = {}
        prog_dict["title"] = elem["title"]["value"]
        prog_dict["description"] = elem["description"]["value"]
        prog_dict["homepage"] = elem["homepage"]["value"]
        prog_dict["repository"] = elem["repository"]["value"]
        prog_dict["year"] = elem["year"]["value"]
        prog_dict["course"] = elem["course"]["value"]
        prog_dict["authors"] = elem["authors"]["value"].split("<!=;=!>")
        prog_dict["ids"] = elem["ids"]["value"].split("<!=;=!>")

        zip_lists = zip(prog_dict["authors"],  prog_dict["ids"])
        ordered_ids = sorted(zip_lists)
        autid = elem["Autmail"]["value"].split("@")[0].replace(".", "_")
        prog_dict["ids"] = [aut_id]
        prog_dict["authors"] = [elem["Firstauthor"]["value"]]
        for x,y in ordered_ids:
            if y != aut_id:
                prog_dict["ids"].append(y)
                prog_dict["authors"].append(x)

        prog_dict["course"] = elem["course"]["value"]
        prog_dict["courseurl"] = elem["courseurl"]["value"]
        cleaned_data.append(prog_dict)
    return cleaned_data, data[0]["Firstauthor"]["value"], data[0]["Autmail"]["value"]


def find_all_authors():
    query = '''prefix dct:<http://purl.org/dc/terms/>
       SELECT
       (group_concat(distinct ?author;separator="<!=;=!>") as ?authors) 
       WHERE{ 
           GRAPH ?g {
               ?g dct:accessRights 'ONLINE'.
               ?pro a foaf:Project;
               dct:creator ?aut.
               ?aut foaf:givenName ?name; foaf:familyName ?surname; foaf:mbox ?mail.

           BIND(CONCAT(CONCAT(STR( ?surname ), ", ", (?name)), "<?=;=?>", REPLACE(strbefore( ?mail, "@" ), "\\\\.", "_")) as ?author).
           }}group by ?g'''
    data = get_query(query)
    cleaned_data = []
    for a in data:
        autlist = a["authors"]["value"].split("<!=;=!>")
        for aut in autlist:
            autdict = {}
            autdata = aut.split("<?=;=?>")
            autdict["text"] = autdata[0]
            autdict["id"] = autdata[1]
            if autdict not in cleaned_data:
                cleaned_data.append(autdict)
    cleaned_data = sorted(cleaned_data, key=lambda k: k['text'])
    return cleaned_data

def change_status(status, graphid):
    graphname = app.config["BASE_URI"] + "graph/" + graphid
    q1 = '''prefix dct:<http://purl.org/dc/terms/>
    WITH <%s>
    DELETE { <%s> dct:accessRights ?r }
    INSERT { <%s> dct:accessRights '%s' }
    WHERE {<%s> dct:accessRights ?r}''' % (graphname, graphname, graphname, status, graphname)
    post_query(q1)

def find_author(id):
    uri = app.config["BASE_URI"] + "person/" + id
    query = ''' SELECT DISTINCT ?Name ?Surname ?Mail 
            Where { Graph ?g {<%s> foaf:givenName ?Name; foaf:familyName ?Surname; foaf:mbox ?Mail.}}'''% uri
    data = get_query(query)
    return data

def change_author(name, surname, id):
    uri = app.config["BASE_URI"] + "person/" + id
    q1 = '''
        DELETE { GRAPH ?g { <%s> foaf:givenName ?Name; foaf:familyName ?Surname } }
        INSERT { GRAPH ?g { <%s> foaf:givenName '%s'; foaf:familyName '%s' } } 
        WHERE { Graph ?g { <%s> foaf:givenName ?Name; foaf:familyName ?Surname}}''' % (uri, uri, name, surname, uri)
    post_query(q1)

def change_all_author(graphid):
    graphname = app.config["BASE_URI"] + "graph/" + graphid
    q = '''
        DELETE { GRAPH ?g { ?aut foaf:givenName ?oldName; foaf:familyName ?oldSurname } }
        INSERT { GRAPH ?g { ?aut foaf:givenName ?Name ; foaf:familyName ?Surname } } 
        WHERE { Graph <%s> { ?aut foaf:givenName ?Name; foaf:familyName ?Surname}
        GRAPH ?g { ?aut foaf:givenName ?oldName; foaf:familyName ?oldSurname }
        FILTER(str(?g) != str(<%s>))
        FILTER(str(?oldName) != str(?Name))
        FILTER(str(?oldSurname) != str(?Surname))
        }''' % (graphname, graphname)
    post_query(q)

def RenameAuthor(name, surname, id):
    uri = app.config["BASE_URI"] + "person/" + id
    q = '''DELETE { GRAPH ?g { <%s> foaf:givenName ?oldName; foaf:familyName ?oldSurname } }
            INSERT { GRAPH ?g { <%s> foaf:givenName "%s" ; foaf:familyName "%s"  } } 
            WHERE { Graph ?g { <%s> foaf:givenName ?oldName; foaf:familyName ?oldSurname}}
            ''' % (uri, uri, name, surname, uri)
    post_query(q)

def get_available():
    query = '''prefix dct:<http://purl.org/dc/terms/>
    prefix doap:<http://usefulinc.com/ns/doap#>
    SELECT ?g ?access ?title ?description ?year ?course ?courseurl ?repository
    (group_concat(distinct ?author;separator="<!=;=!>") as ?authors) 
    (group_concat(distinct ?id;separator="<!=;=!>") as ?ids)
    (group_concat(distinct ?hpage;separator="<!=;=!>") as ?homepage)
    WHERE{ 
        GRAPH ?g {
            ?g dct:accessRights ?access.
            ?pro a foaf:Project;
            dct:title ?title;
            dct:description ?description;
            doap:GitRepository ?repository;
            dct:creator ?aut;
            dct:subject ?courseEntity.
            OPTIONAL {?pro foaf:homepage ?hpage.}
            ?aut foaf:givenName ?name; foaf:familyName ?surname; foaf:mbox ?mail.
            ?courseEntity dct:title ?course; foaf:homepage ?courseurl; dct:coverage ?period.
            ?period rdfs:label ?year.
        FILTER(NOT EXISTS {?g dct:accessRights 'SUSPENDED'.})
        BIND(CONCAT(STR( ?surname ), ", ", (?name)) as ?author).
        BIND(REPLACE(strbefore( ?mail, "@" ), "\\\\.", "_") as ?id )
        }

        }group by ?g ?access ?title ?description ?year ?course ?courseurl ?repository'''
    data = get_query(query)

    cleaned_data = []

    for elem in data:
        prog_dict = {}
        prog_dict["graph"] = elem["g"]["value"].replace("https://w3id.org/DHDY/graph/", "")
        prog_dict["access"] = elem["access"]["value"]
        prog_dict["title"] = elem["title"]["value"]
        prog_dict["description"] = elem["description"]["value"]
        prog_dict["homepage"] = elem["homepage"]["value"]
        prog_dict["repository"] = elem["repository"]["value"]
        prog_dict["year"] = elem["year"]["value"]
        prog_dict["course"] = elem["course"]["value"]
        prog_dict["authors"] = elem["authors"]["value"].split("<!=;=!>")
        prog_dict["ids"] = elem["ids"]["value"].split("<!=;=!>")

        zip_lists = zip(prog_dict["authors"], prog_dict["ids"])
        ordered_ids = sorted(zip_lists)
        prog_dict["ids"] = []
        prog_dict["authors"] = []
        for x, y in ordered_ids:
            prog_dict["ids"].append(y)
            prog_dict["authors"].append(x)

        prog_dict["course"] = elem["course"]["value"]
        prog_dict["courseurl"] = elem["courseurl"]["value"]
        cleaned_data.append(prog_dict)
    return cleaned_data


def get_suspended():
    query = '''prefix dct:<http://purl.org/dc/terms/>
    prefix doap:<http://usefulinc.com/ns/doap#>
    SELECT ?g ?title ?publisher ?description ?year ?course ?courseurl ?repository
    (group_concat(distinct ?author;separator="<!=;=!>") as ?authors) 
    (group_concat(distinct ?id;separator="<!=;=!>") as ?ids)
    (group_concat(distinct ?hpage;separator="<!=;=!>") as ?homepage)
    WHERE{ 
        GRAPH ?g {
            ?g dct:accessRights 'SUSPENDED'.
            ?g dct:publisher ?publisher.
            ?pro a foaf:Project;
            dct:title ?title;
            dct:description ?description;
            doap:GitRepository ?repository;
            dct:creator ?aut;
            dct:subject ?courseEntity.
            OPTIONAL {?pro foaf:homepage ?hpage.}
            ?aut foaf:givenName ?name; foaf:familyName ?surname; foaf:mbox ?mail.
            ?courseEntity dct:title ?course; foaf:homepage ?courseurl; dct:coverage ?period.
            ?period rdfs:label ?year.

        BIND(CONCAT(STR( ?surname ), ", ", (?name)) as ?author).
        BIND(REPLACE(strbefore( ?mail, "@" ), "\\\\.", "_") as ?id )
        }}group by ?g ?title ?publisher ?description ?year ?course ?courseurl ?repository'''
    data = get_query(query)

    cleaned_data = []

    for elem in data:
        prog_dict = {}
        prog_dict["title"] = elem["title"]["value"]
        prog_dict["graph"] = elem["g"]["value"].replace("https://w3id.org/DHDY/graph/", "")
        prog_dict["publisher"] = elem["publisher"]["value"]
        prog_dict["description"] = elem["description"]["value"]
        prog_dict["homepage"] = elem["homepage"]["value"]
        prog_dict["repository"] = elem["repository"]["value"]
        prog_dict["year"] = elem["year"]["value"]
        prog_dict["course"] = elem["course"]["value"]
        prog_dict["authors"] = elem["authors"]["value"].split("<!=;=!>")
        prog_dict["ids"] = elem["ids"]["value"].split("<!=;=!>")

        zip_lists = zip(prog_dict["authors"], prog_dict["ids"])
        ordered_ids = sorted(zip_lists)
        prog_dict["ids"] = []
        prog_dict["authors"] = []
        for x, y in ordered_ids:
            prog_dict["ids"].append(y)
            prog_dict["authors"].append(x)

        prog_dict["course"] = elem["course"]["value"]
        prog_dict["courseurl"] = elem["courseurl"]["value"]
        cleaned_data.append(prog_dict)
    return cleaned_data

def dump():
    query = '''SELECT ?x ?y ?z ?g where { GRAPH ?g {?x ?y ?z}}'''
    data = get_query(query)
    if data:
        g = ConjunctiveGraph()
        for q in data:
            if q['z']['type'] == 'uri':
                g.addN([(URIRef(q['x']['value']), URIRef(q['y']['value']), URIRef(q['z']['value']), URIRef(q['g']['value']))])
            else:
                g.addN([(URIRef(q['x']['value']), URIRef(q['y']['value']), Literal(q['z']['value']),URIRef(q['g']['value']))])
        g.serialize("dump/dump.nq", format="nquads")



#Ancillary functions
def post_query (query):
    ts.setMethod('POST')
    ts.setQuery(query)
    ts.query()

def get_query(query):
    ts.setQuery(query)
    result = ts.query().convert() .get("results").get("bindings")
    return result