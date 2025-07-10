import logging
import os
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_migrate import Migrate
from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize extensions
db = SQLA(app)
migrate = Migrate(app, db)
appbuilder = AppBuilder(app, db.session)

# Import models (must be after db initialization)
try:
    from . import models
except ImportError:
    pass

# Configure logging
if not app.debug and not app.testing:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = logging.FileHandler(app.config.get('LOG_FILE', 'logs/ct_scanner.log'))
    file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    app.logger.info('CT Scanner App startup')
