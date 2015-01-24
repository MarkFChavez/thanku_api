class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), unique=True)
  email = db.Column(db.String(64), unique=True)
  password = db.Column(db.String(255))

  def __repr__(self):
    return "<User %r>" % self.name
