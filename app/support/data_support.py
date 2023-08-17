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


import csv, re, json, os
from urllib import parse
from app import app

#This function create a dictionary with data curations
def parse_form(form, time):
    data = {}
    for url_k in form:
        v = form[url_k]
        ks = []
        while url_k:
            if '[' in url_k:
                k, r = url_k.split('[', 1)
                ks.append(k)
                if r[0] == ']':
                    ks.append('')
                url_k = r.replace(']', '', 1)
            else:
                ks.append(url_k)
                break
        sub_data = data
        for i, k in enumerate(ks):
            if k.isdigit():
                k = int(k)
            if i+1 < len(ks):
                if not isinstance(sub_data, dict):
                    break
                if k in sub_data:
                    sub_data = sub_data[k]
                else:
                    sub_data[k] = {}
                    sub_data = sub_data[k]
            else:
                if isinstance(sub_data, dict):
                    sub_data[k] = v
    data["Title"] = clean_title(data["Title"])
    data["Description"] = ' '.join(data["Description"].split())
    data["Date"] = time.strftime('%Y-%m-%d')
    data["Responsible"] = data["Responsible"].lower()
    for aut in data["Aut"]:
        data["Aut"][aut]["Name"] = ' '.join(data["Aut"][aut]["Name"].title().split())
        data["Aut"][aut]["Surname"] = ' '.join(data["Aut"][aut]["Surname"].title().split())
        data["Aut"][aut]["Mail"] = data["Aut"][aut]["Mail"].lower()
    data["Id"] = project_id(data, time)
    data["Course_url"] = find_page(data["Course"], data["Year"])
    #json_store(data, data["Id"])
    return data

def remove_json(id):
    path = os.path.join(app.config["TEMP_PATH"], id + ".json")
    os.remove(path)

def retrieve_json(id):
    try:
        path = os.path.join(app.config["TEMP_PATH"], id + ".json")
        with open(path, "r") as read_file:
            data = json.load(read_file)
            return data
    except:
        return None

def json_store (data, filename):
    path = os.path.join(app.config["TEMP_PATH"], filename + ".json")
    with open(path, 'w') as file:
        json.dump(data, file)


def update_courses(file, data_path):
    new_data = cleaning_course(process_file(file))
    data = process_data(data_path)
    data = unique(data + new_data)
    with open(data_path, "w", newline='') as toWrite:
        writer = csv.DictWriter(toWrite, fieldnames=["AcademicYear", "CourseTitle", "CoursePage"])
        writer.writeheader()
        writer.writerows(data)
        toWrite.close()
    return

def prepare_data(data_path):
    newlist = []
    yearset = set()
    data = process_data(data_path)
    for row in data:
        if row["AcademicYear"] not in yearset:
            yearset.add(row["AcademicYear"])
            yeardict = dict()
            yeardict["year"] = row["AcademicYear"]
            yeardict["courses"] = list()
            yeardict["courses"].append(row["CourseTitle"])
            newlist.append(yeardict)
        else:
            for x in newlist:
                if x["year"] == row["AcademicYear"]:
                    x["courses"].append(row["CourseTitle"])
    return newlist

def clean_title(title):
    title = ' '.join(title.split())
    if title.isupper():
        title = title.lower()
    words = title.split()
    for pos, w in enumerate(words):
        if any(x.isupper() for x in w):
            pass
        else:
            words[pos] = w.title()
    newtitle = " ".join(words)
    return newtitle


def project_id(data, time):
    main_text = re.sub('[^A-Za-z0-9]+', '', data["Title"].replace(" ", "").lower())[:70]
    proj_id = main_text + time.strftime('%Y%m%d%H%M%S')
    return parse.quote(proj_id, safe="")

def process_data(source_csv_file_path):
    with open(source_csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [dict(x) for x in reader]
    return data

def process_file(file):
    reader = csv.DictReader(file, delimiter=',')
    data = [x for x in reader]
    return data

def unique(list):
    newlist = []
    for x in list:
        if x and x not in newlist:
            newlist.append(x)
    return newlist

def cleaning_course(list):
    for row in list:
        row["CourseTitle"] = clean_title(row["CourseTitle"])
    return list

def removeCSV(year, name, data_path):
    data = process_data(data_path)
    remove_index = None
    for pos,row in enumerate(data):
        if row["AcademicYear"] == year and row["CourseTitle"] == name:
            remove_index = pos
            break
    if remove_index is not None:
        data.pop(remove_index)
        with open(data_path, "w", newline='') as toWrite:
            writer = csv.DictWriter(toWrite, fieldnames=["AcademicYear", "CourseTitle", "CoursePage"])
            writer.writeheader()
            writer.writerows(data)
            toWrite.close()
    return


def find_page(course, year):
    data = process_data(app.config["CSV_PATH"])
    for row in data:
        if row["AcademicYear"] == year and row["CourseTitle"] == course:
            return row["CoursePage"]