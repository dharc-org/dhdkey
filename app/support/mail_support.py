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


from app import app
from flask import render_template
from flask_mail import Mail, Message
import jwt
from threading import Thread

MODE_TO_FILENAME_DICT = {
    'upload': 'confirmation',
    'update': 'confirmation-update',
    'delete': 'confirmation-delete'
}

MODE_TO_TOPIC_DICT = {
    'upload': 'DHDKey! Project Confirmation',
    'update': 'DHDKey! Project Update',
    'delete': 'DHDKey! Project Deletion'
}

mail = Mail(app)
def user_confirmation_email(data, mode='upload'):
    title = data["Title"]
    address = data["Responsible"]
    filename = data["Id"]
    token = get_token(filename)
    send_email(MODE_TO_TOPIC_DICT[mode],
               recipients=[address],
               text_body=render_template(f'email/{MODE_TO_FILENAME_DICT[mode]}.txt',
                                         title=title,
                                         token=token),
               html_body=render_template(f'email/{MODE_TO_FILENAME_DICT[mode]}.html',
                                         title=title,
                                         token=token)
                )


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    #Threading to avoid slow process
    Thread(target=send_async_email, args=(app, msg)).start()


#function to generate users' tokens
def get_token(data):
    # more info at https://jwt.io/introduction/
    payload = {'data': data}
    return jwt.encode(
        payload,
        app.config['SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM']).decode('utf-8')

#function to verify users' tokens
def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])
        data = payload['data']
    except:
        return None
    return data