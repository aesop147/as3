from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import make_response
from flask import request
from flask.json import jsonify
from functools import wraps
from flask_migrate import Migrate
import jwt
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:dias12345@localhost/python_db"
app.config['SECRET_KEY'] = 'thisismyflasksecretkey'
app.debug = True
db = SQLAlchemy(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


@app.route('/unprotected')
def unprotected():
    return jsonify({'message' : 'Anyone can view this!'})

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message' : 'This is only available for people with valid tokens.'})



class Login(db.Model):
    __tablename__ = 'Login'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String())
    password = db.Column(db.String())
    token = db.Column(db.Integer())

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        return f"<Hello {self.login}>"

@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'secret':
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=15)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

login1 = Login('Dias', 'dias12345')
login2 = Login('Farid', 'farid12345')
login3 = Login('Zhalgas', 'zhalgas12345')
db.session.add(login1)
db.session.add(login2)
db.session.add(login3)
db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
