from flask import Flask, Blueprint
from flask.ext.script import Manager

app = Flask(__name__)
manager = Manager(app)

api = Blueprint("api", __name__)

def create_app(config_name):
  from .api_1_0 import api as api_1_0_blueprint
  app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")

@app.route("/")
def index():
  return "Hello world!"

if __name__ == "__main__":
  manager.run()
