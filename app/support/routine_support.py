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


from app.support import data_support, SPARQL_support
import os
from app import app
from datetime import datetime

def routine ():
    SPARQL_support.dump()
    expires()


def expires():
    for filename in os.listdir(app.config["TEMP_PATH"]):
        name = filename.replace(".json", "")
        date = name[-14:]
        oldtime = datetime.strptime(date, '%Y%m%d%H%M%S')
        nowtime = datetime.now()
        diff = nowtime - oldtime
        if diff.days > 1:
            data_support.remove_json(name)
