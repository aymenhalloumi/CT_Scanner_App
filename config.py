import os
from flask_appbuilder.security.manager import AUTH_DB

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'ct_install.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_NAME = "CT Scanner Manager"
    AUTH_TYPE = AUTH_DB

config = {
    'development': Config,
    'default': Config
}
