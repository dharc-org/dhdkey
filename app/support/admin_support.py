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


from app import app, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

adminUs = generate_password_hash(app.config["USERNAME"])
pword = generate_password_hash(app.config["PASSWORD"])


class User(UserMixin):
    def __init__(self, username):
        self.name = username

    @property
    def id(self):
        return self.name


@login.user_loader
def load_user(username):
    return User(username)


def verify_password(username, password):
    if check_password_hash(adminUs, username):
        return check_password_hash(pword, password)
    return False


