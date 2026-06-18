from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import os

db = SQLAlchemy()
DB_NAME = "database.db"
login_manager = LoginManager()


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-this'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page'

    from .models import User, Event, Booking, Comment
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    from .views import views
    from .auth import auth
    from .errors import errors
    
    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(errors)

    return app
