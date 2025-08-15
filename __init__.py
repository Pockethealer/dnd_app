from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
)

db =SQLAlchemy(metadata=metadata)
DB_NAME= "database.db"

def create_app():
    app = Flask(__name__)
    UPLOAD_FOLDER = path.join(app.root_path, 'static', 'media')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY']= '#TODO'
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME}'
    db.init_app(app)
    app.json.sort_keys = False

    

    from .views import views
    from .auth import auth
    from .admin import admin
    from .manage_entries import manage_entries
    from .page_editor import page_editor
    from .upload import upload
    from .pull import pull

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')
    app.register_blueprint(manage_entries, url_prefix='/')
    app.register_blueprint(page_editor, url_prefix='/')
    app.register_blueprint(upload, url_prefix='/')
    app.register_blueprint(pull, url_prefix='/')


    from .models import User

    create_database(app)

    login_manager=LoginManager()
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    migrate = Migrate(app, db, render_as_batch=True)

    return app

def create_database(app):
    basedir = path.abspath(path.join(path.dirname(__file__), '..'))
    db_path = path.join(basedir, 'instance', DB_NAME)
    #print("Checking DB at:", path.abspath(db_path))
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
            print('Created database')
