from flask import Flask, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY']='123'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://capstone:capstone@localhost/capstone"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

db = SQLAlchemy(app)
from app import views







