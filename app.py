from tempfile import template
from auth.routes_auth import auth_bp
from books.routes_books import books_bp
from friends.friends_routes import friends_bp
from auth.models_user import User
from flask import Flask

from core.extensions import db,migrate,bcrypt,login_manager
from flask_session import Session
import os
from dotenv import load_dotenv
load_dotenv(override=True)

def create_app():
    app =Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/')
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'

    db.init_app(app)
    migrate.init_app(app,db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    app.secret_key=os.getenv('key')
    app.config['SESSION_TYPE']='sqlalchemy'
    app.config['SESSION_SQLALCHEMY']=db
    Session(app)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(books_bp)
    
    return app



