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


from rdflib import ConjunctiveGraph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD, DCTERMS, FOAF, RDFS
from .data_support import process_data
from app import app
from urllib import parse
import string

def ProjectRdf(data):
    g = ConjunctiveGraph()
    graph = URIRef(app.config["BASE_URI"] + "graph/" + data["Id"])
    proj = URIRef(app.config["BASE_URI"] + "project/" + data["Id"])
    DOAP = Namespace("http://usefulinc.com/ns/doap#")
    g.addN([(proj, RDF.type, FOAF.Project, graph)])
    g.addN([(proj, DCTERMS.title, Literal(data["Title"]), graph)])
    g.addN([(proj, DCTERMS.description, Literal(data["Description"]), graph)])
    g.addN([(proj, DOAP.GitRepository, URIRef(data["Repository"]), graph)])
    if data["Homepage"]:
        g.addN([(proj, FOAF.homepage, URIRef(data["Homepage"]), graph)])

    #authors
    for aut in data["Aut"]:
        aut_uri = URIRef(app.config["BASE_URI"] + "person/" + parse.quote(data["Aut"][aut]["Mail"].split("@")[0].replace(".", "_"), safe=""))
        g.addN([(proj, DCTERMS.creator, aut_uri, graph)])
        g.addN([(aut_uri, RDF.type, FOAF.Person, graph)])
        g.addN([(aut_uri, FOAF.givenName, Literal(data["Aut"][aut]["Name"]), graph)])
        g.addN([(aut_uri, FOAF.familyName, Literal(data["Aut"][aut]["Surname"]), graph)])
        g.addN([(aut_uri, FOAF.mbox, Literal(data["Aut"][aut]["Mail"]), graph)])

    #course
    course_id = parse.quote(data["Course"].replace(" ", "").replace(string.punctuation, ""), safe="")[:30]
    course_uri = URIRef(app.config["BASE_URI"] + "course/" + data["Year"].replace("-","_") + "/" + course_id)
    g.addN([(proj, DCTERMS.subject, course_uri, graph)])
    g.addN([(course_uri, RDF.type, DCTERMS.MethodOfInstruction, graph)])
    g.addN([(course_uri, DCTERMS.title, Literal(data["Course"]), graph)])
    g.addN([(course_uri, FOAF.homepage, URIRef(data["Course_url"]), graph)])

    #Year
    year_uri = URIRef(app.config["BASE_URI"] + "year/" + data["Year"].replace("-","_"))
    g.addN([(course_uri, DCTERMS.coverage, year_uri, graph)])
    TIME = Namespace("http://www.w3.org/2006/time#")
    g.addN([(year_uri, RDF.type, TIME.TemporalEntity, graph)])
    g.addN([(year_uri, RDFS.label, Literal(data["Year"]), graph)])

    #Graph Metadata
    g.addN([(graph, DCTERMS.accessRights, Literal("SUSPENDED"), graph)])
    g.addN([(graph, DCTERMS.dateSubmitted, Literal(str(data["Date"]), datatype=XSD.date), graph)])
    pub_uri = URIRef(app.config["BASE_URI"] + "person/" + data["Responsible"].split("@")[0].replace(".", "_"))
    g.addN([(graph, DCTERMS.publisher, pub_uri, graph)])

    return g


def find_page(course, year):
    data = process_data(app.config["CSV_PATH"])
    for row in data:
        if row["AcademicYear"] == year and row["CourseTitle"] == course:
            return URIRef(row["CoursePage"])
