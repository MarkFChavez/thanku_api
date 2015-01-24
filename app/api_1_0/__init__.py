from flask import Flask, Blueprint
from flask.ext.script import Manager

app = Flask(__name__)
manager = Manager(app)

api = Blueprint("api", __name__)

from . import databases, users

def create_app(config_name):
  from .api_1_0 import api as api_1_0_blueprint
  app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")

if __name__ == "__main__":
  manager.run()
