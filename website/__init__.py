from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import os
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_database(app):
    if not os.path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
            print("Database Created!")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jflkdsjfalksjfdsa jfsdlkjfdsljfa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .blends import blends
    from .auth import auth
    from .builds import builds

    app.register_blueprint(blends, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(builds, url_prefix='/')

    from .models import PowderBlends, Users

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    return app
