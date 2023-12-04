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



#this files contains different URL actions implemented
from app import app#, scheduler
from app.support import data_support, mail_support, admin_support, SPARQL_support, rdf_support#, routine_support
from flask import render_template, request, redirect, url_for, flash, Response
from datetime import datetime
from flask_login import current_user, login_user, logout_user, login_required
from urllib import parse

#dump everyday at 3 A.M. (italian time zone)
#scheduler.add_job(routine_support.routine, 'cron', hour='3')

@app.context_processor
def inject_template_scope():
    injections = dict()

    def cookies_check():
        value = request.cookies.get('cookie_consent')
        return value == 'true'
    injections.update(cookies_check=cookies_check)

    return injections

#Index route
@app.route('/')
@app.route('/index')
def index():
    try:
        id = request.args['id']
        search = request.args['search']
        data, autname, autmail = SPARQL_support.by_author(id)
        autdata = SPARQL_support.find_all_authors()
        name = id
        mail = None
        if data:
            name = autname
            mail = autmail
        return render_template('projects.html', title=name, data=data, name=name, mail=mail, autdata=autdata, author=True, search=search)
    except:
        data = SPARQL_support.get_all("ONLINE")
        autdata = SPARQL_support.find_all_authors()
        return render_template('index.html', title="Home", data=data, autdata=autdata)

@app.route('/info')
def info():
    return render_template('documents/info.html', title="Info")

@app.route('/documentation')
def documentation():
    return render_template('documents/documentation.html', title="Documentation")

@app.route('/privacy')
def privacy():
    return render_template('documents/privacy.html', title="Privacy Policy & Terms of Service")

@app.route('/projects')
def projects():
    if 'mail' in request.args.keys():
        print(request.args['mail'])
        aut_id = parse.quote(request.args['mail'].split("@")[0].replace(".", "_").lower(), safe="")
        try:
            data, autname, autmail = SPARQL_support.by_author(aut_id, 'SUSPENDED')
        except IndexError as _:
            flash('not found')
            return redirect(url_for('index'))
        print(data)
        mail_support.suspended_details_email(data, address=request.args['mail'].lower())
        # confirmationemail = jsondata["Responsible"]
        flash(request.args['mail'], 'details sent')
        return redirect(url_for('index'))

    if 'id' in request.args.keys():
        id = request.args['id']
        data, autname, autmail = SPARQL_support.by_author(id)
        print(data)
        autdata = SPARQL_support.find_all_authors()
        name = id
        mail = None
        search = None
        if 'search' in request.args.keys():
            search = request.args['search']
        if data:
            name = autname
            mail = autmail
        return render_template('projects.html', title=name, data=data, name=name, mail=mail, autdata=autdata, author=True, search=search)
    else:
        data = SPARQL_support.get_all("ONLINE")
        autdata = SPARQL_support.find_all_authors()
        search=''
        if 'search' in request.args.keys():
            search = request.args['search']
        return render_template('projects.html', title='Projects', data=data, name=None, autdata=autdata, author=False, search=search)


@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        if request.form["action"] in ["Edit project", "Delete project"]:
            id = request.args['id']
            data = [
                project for project in SPARQL_support.get_available() if project['graph'] == id
                ][0]
            print(data)
            authors_data = []
            for aut in data['ids']:
                _, aut_fullname, aut_mail = SPARQL_support.by_author(aut)
                print(f"full_name: {aut_fullname}")
                aut_surname, aut_name  = (aut_fullname.split(',')[0].strip(), aut_fullname.split(',')[1].strip())
                authors_data.append(
                    {
                        "name": aut_name,
                        "surname": aut_surname,
                        "mail": aut_mail
                    }
                )
            if len(data):
                courses_data = data_support.prepare_data(app.config['CSV_PATH'])
                if request.form["action"] == 'Edit project':
                    return render_template('update.html', title='Update', courses_data=courses_data, project_data=data, authors_data=authors_data)
                elif request.form["action"] == 'Delete project':
                    return render_template('delete.html', title='Update', courses_data=courses_data, project_data=data, authors_data=authors_data)
        else:
            print('post')
            data = request.form
            print(data)
            time = datetime.now()
            print(request.form["graphid"])
            request_mode = request.form["mode"]
            jsondata = data_support.parse_form(data, time, force_id=request.form["graphid"])
            print(jsondata)
            mail_support.user_confirmation_email(jsondata, mode=request_mode)
            confirmationemail = jsondata["Responsible"]
            flash(confirmationemail, 'sended')
            return redirect(url_for('index'))

                # return redirect(url_for('update', id=id))
            # print(request.form)
    return redirect(url_for('projects'))


#update route
# @app.route('/update/<id>', methods=['GET', 'POST'])
# def update(id):
#     print(id)
#     if request.method == 'POST':
#         print('post')
#         data = request.form
#         time = datetime.now()
#         jsondata = data_support.parse_form(data, time)
#         mail_support.user_confirmation_email(jsondata)
#         confirmationemail = jsondata["Responsible"]
#         flash(confirmationemail, 'sended')
#         return redirect(url_for('index'))
#     else:
#         courses_data = data_support.prepare_data(app.config['CSV_PATH'])
#         data = [
#                 project for project in SPARQL_support.get_available() if project['graph'] == id
#                 ][0]
#         authors_data = []
#         for aut in data['ids']:
#             _, aut_fullname, aut_mail = SPARQL_support.by_author(aut)
#             aut_name, aut_surname = (aut_fullname.split(',')[0], aut_fullname.split(',')[1])
#             authors_data.append(
#                 {
#                     "name": aut_name,
#                     "surname": aut_surname,
#                     "mail": aut_mail
#                 }
#             )
#         if len(data):
#             courses_data = data_support.prepare_data(app.config['CSV_PATH'])
#         return render_template('update.html', title='Update', courses_data=courses_data, project_data=data, authors_data=authors_data)


#confirmation route, token required
@app.route('/confirmation-update/<token>', methods=['GET', 'POST'])
def update_confirmation(token):
    print('here')
    id = mail_support.verify_token(token)
    # print(id)
    if not id:
        flash('fail')
        print('fail')
        return redirect(url_for('index')) #wrong token
    if SPARQL_support.expired(id):
        flash("already")
        print('already')
        return redirect(url_for('index'))   #expired token
    data = data_support.retrieve_json(id)
    print(data)
    if not data:
        flash('expired')
        print('here')
        print('expired')
        return redirect(url_for('index'))  # Do not exist
    #confirmation/rejection
    if request.method == 'POST':
        print('posting form')
        if request.form["selection"] == "confirm":
            print('trying to confirm')
            SPARQL_support.delete_graph(data['graph'])
            # SPARQL_support.dump()
            print('deleted graph')

            rdf_data = rdf_support.ProjectRdf(data,'ONLINE')
            SPARQL_support.add_data(rdf_data, quad=True)
            SPARQL_support.change_status("ONLINE", id)
            SPARQL_support.change_all_author(id)
            data_support.remove_json(id)
            SPARQL_support.dump()
            print('updated')
            flash("updated")
        elif request.form["selection"] == "reject":
            data_support.remove_json(id)
            print('rejected')
        return redirect(url_for('index'))
    
    routing_data={
        'url_for': 'update_confirmation',
        'title_text': 'Updated Data Summary'
    }
    return render_template('confirmation_form.html', 
                           title='Update confirmation', 
                           token=token, 
                           data=data,
                           routing_data=routing_data)


@app.route('/confirmation-delete/<token>', methods=['GET', 'POST'])
def delete_confirmation(token):
    print('here')
    id = mail_support.verify_token(token)
    # print(id)
    if not id:
        flash('fail')
        print('fail')
        return redirect(url_for('index')) #wrong token
    if SPARQL_support.expired(id):
        flash("already")
        print('already')
        return redirect(url_for('index'))   #expired token
    data = data_support.retrieve_json(id)
    print(data)
    if not data:
        flash('expired')
        print('here')
        print('expired')
        return redirect(url_for('index'))  # Do not exist
    #confirmation/rejection
    if request.method == 'POST':
        print('posting form')
        if request.form["selection"] == "confirm":
            print('trying to confirm')
            SPARQL_support.delete_graph(data['graph'])
            # SPARQL_support.dump()
            print('deleted graph')

            # rdf_data = rdf_support.ProjectRdf(data,'ONLINE')
            # SPARQL_support.add_data(rdf_data, quad=True)
            # SPARQL_support.change_status("ONLINE", id)
            # SPARQL_support.change_all_author(id)
            data_support.remove_json(id)
            SPARQL_support.dump()
            print('deleted')
            flash("deleted")
        elif request.form["selection"] == "reject":
            data_support.remove_json(id)
            print('rejected')
        return redirect(url_for('index'))
    
    routing_data={
        'url_for': 'delete_confirmation',
        'title_text': 'Data summary of the project to delete'
    }
    return render_template('confirmation_form.html', 
                           title='Update confirmation', 
                           token=token, 
                           data=data,
                           routing_data=routing_data)

#NO CONFIRMATION MAIL
'''
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            data = request.form
            time = datetime.now()
            jsondata = data_support.parse_form(data, time)
            rdf_data = rdf_support.ProjectRdf(jsondata)
            SPARQL_support.add_data(rdf_data, quad=True)
            flash("confirmed")
            SPARQL_support.dump()
        except:
            flash("error")
        return redirect(url_for('index'))
    else:
        courses_data = data_support.prepare_data(app.config['CSV_PATH'])
        return render_template('upload.html', title='Upload', courses_data=courses_data)
'''

#upload route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        data = request.form
        # print(data)
        time = datetime.now()
        jsondata = data_support.parse_form(data, time)
        mail_support.user_confirmation_email(jsondata)
        confirmationemail = jsondata["Responsible"]
        flash(confirmationemail, 'sended')
        return redirect(url_for('index'))
    else:
        courses_data = data_support.prepare_data(app.config['CSV_PATH'])
        return render_template('upload.html', title='Upload', courses_data=courses_data)
    



#confirmation route, token required
@app.route('/confirmation/<token>', methods=['GET', 'POST'])
def confirmation(token):
    id = mail_support.verify_token(token)
    # print(id)
    if not id:
        flash('fail')
        return redirect(url_for('index')) #wrong token
    if SPARQL_support.expired(id):
        flash("already")
        return redirect(url_for('index'))   # expired token
    data = data_support.retrieve_json(id)
    # print(data)
    if not data:
        flash('expired')
        return redirect(url_for('index'))  # Do not exist
    #confirmation/rejection
    if request.method == 'POST':
        if request.form["selection"] == "confirm":
            rdf_data = rdf_support.ProjectRdf(data)
            SPARQL_support.add_data(rdf_data, quad=True)
            data_support.remove_json(id)
            flash("confirmed")
        elif request.form["selection"] == "reject":
            data_support.remove_json(id)
        return redirect(url_for('index'))
    routing_data={
        'url_for': 'confirmation',
        'title_text': 'Uploaded Data Summary'
    }
    return render_template('confirmation_form.html', title='Confirmation', token=token, data=data, routing_data=routing_data)


#Admin route
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        if admin_support.verify_password(username, password):
            user = admin_support.load_user(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('admin.html', title='Admin Access')


@app.route('/manager/confirm', methods=['GET','POST'])
@login_required
def AdminConfirm():
    data = SPARQL_support.get_suspended()
    return render_template('admin/AdminConfirm.html', data=data, active="confirm", title='Manager')

@app.route('/manager/confirm/project/', methods=['POST'])
@login_required
def AdminConfirmProject():
    id = request.args['id']
    if request.method == 'POST':
        if request.form["action"] == "CONFIRM":
            SPARQL_support.change_status("ONLINE", id)
            SPARQL_support.change_all_author(id)
        elif request.form["action"] == "REJECT":
            SPARQL_support.delete_graph(id)
        SPARQL_support.dump()
    return redirect(url_for('AdminConfirm'))


@app.route('/manager/edit', methods=['GET', 'POST'])
@login_required
def AdminEdit():
    data = SPARQL_support.get_available()
    return render_template('admin/AdminEdit.html',  data=data, active="edit", title='Manager')

@app.route('/manager/edit/project/', methods=['POST'])
@login_required
def AdminEditProject():
    id = request.args['id']
    if request.method == 'POST':
        if request.form["action"] == "GO ONLINE":
            SPARQL_support.change_status("ONLINE", id)
        elif request.form["action"] == "GO OFFLINE":
            SPARQL_support.change_status("OFFLINE", id)
        elif request.form["action"] == "REMOVE":
            SPARQL_support.delete_graph(id)
        SPARQL_support.dump()
    return redirect(url_for('AdminEdit'))

@app.route('/manager/courses', methods=['GET', 'POST'])
@login_required
def AdminCourses():
    if request.method == 'POST':
        file = (request.files['file']).read().decode("utf-8").splitlines()
        data_support.update_courses(file, app.config["CSV_PATH"])
    return render_template('admin/AdminCourse.html', active="courses", title='Manager')

@app.route('/manager/edit_author', methods=['GET', 'POST'])
@login_required
def AdminAuthorEdit():
    if request.method == 'POST':
        name = ' '.join(request.form["Name"].title().split())
        surname = ' '.join(request.form["Surname"].title().split())
        mail = request.form["Mail"].lower()
        id = mail.split("@")[0].replace(".", "_")
        SPARQL_support.RenameAuthor(name, surname, id)
    return render_template('admin/AdminAuthorEdit.html', active="editauthor", title='Manager')

@app.route('/manager/download', methods=['GET', 'POST'])
@login_required
def AdminDownload():
    return render_template('admin/AdminDownload.html', active="download", title='Manager')

@app.route('/manager/download/dump', methods=['GET', 'POST'])
@login_required
def DumpDownload():
    SPARQL_support.dump()
    with open("dump/dump.nq") as fp:
            nt = fp.read()
            return Response(
                nt,
                mimetype="text",
                headers={"Content-disposition":
                             "attachment; filename=DHDKey_Dump.nq"})


@app.route('/manager/download/csv', methods=['GET', 'POST'])
@login_required
def CSVDownload():
    with open("courses/courses.csv") as fp:
            csv = fp.read()
            return Response(
                csv,
                mimetype="text/csv",
                headers={"Content-disposition":
                             "attachment; filename=courses.csv"})

'''@app.errorhandler(401)
def custom_401(error):
    flash('login')
    return redirect(url_for('index'))'''

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

import logging
import traceback

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger()

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    error_dict = {
        'code': error.code,
        'description': error.description,
        'stack_trace': traceback.format_exc()
    }
    log_msg = f"HTTPException {error_dict}, Description: {error_dict.keys()}, Stack trace: "
    logger.log(level=0, msg=log_msg)
    response = jsonify(error_dict)
    response.status_code = error.code
    return response