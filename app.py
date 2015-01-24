import os
from flask import Flask, jsonify, g, request
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

basedir = os.path.abspath(os.path.dirname(__file__))

api = Flask(__name__)
api.config["SECRET_KEY"] = "this is an entry for the awesome app contest"
api.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
api.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
db = SQLAlchemy(api)
manager = Manager(api)
auth = HTTPBasicAuth()

class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), unique=True)
  name = db.Column(db.String(128))
  password_hash = db.Column(db.String(128))

  def __repr__(self):
    return "<User %r>" % self.name

  def to_json(self):
    json_user = {
      "id": self.id,
      "name": self.name,
      "username": self.username
    }

    return json_user

  def hash_password(self, password):
    self.password_hash = pwd_context.encrypt(password)

  def verify_password(self, password):
    return pwd_context.verify(password, self.password_hash)

  def generate_auth_token(self, expiration = 600):
    s = Serializer(api.config["SECRET_KEY"], expires_in = expiration)
    return s.dumps({ "id": self.id })

  @staticmethod
  def verify_auth_token(token):
    s = Serializer(api.config["SECRET_KEY"])

    try:
      data = s.loads(token)
    except SignatureExpired:
      return None
    except BadSignature:
      return None

    user = User.query.get(data["id"])
    return user

@auth.verify_password
def verify_password(username_or_token, password):
  user = User.verify_auth_token(username_or_token)

  if not user:
    user = User.query.filter_by(username = username_or_token).first()
    if not user or not user.verify_password(password):
      return False

  g.user = user

  return True

@api.route("/api/v1.0/token")
@auth.login_required
def get_auth_token():
  token = g.user.generate_auth_token()
  return jsonify({ "token": token.decode("ascii") })

@api.route("/api/v1.0/signin", methods=["POST"])
def signin():
  user = User.query.filter_by(username = request.args["username"]).first()
  if user.verify_password(request.args["password"]):
    return jsonify({ "status": "ok" })

  return jsonify({ "status": "error" })

@api.route("/api/v1.0/thank/<int:user_id>", methods=["POST"])
@auth.login_required
def thank_user(user_id):
  user = g.user
  recipient = User.query.get(user_id)

  return jsonify({ "status": "ok", "user": user.to_json(), "recipient": recipient.to_json() })

if __name__ == "__main__":
  manager.run()

