import os
from flask import Flask

danibook = Flask(__name__)
danibook.secret_key = os.environ.get("SECRET_KEY")

import routes