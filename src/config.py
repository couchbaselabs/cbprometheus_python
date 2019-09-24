import logging
import os

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'you will never guess'
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_LOCATION = '../logs/messaging.log'
    LOGGING_LEVEL = logging.INFO
    CB_DATABASE = os.environ.get("CB_DATABASE", "localhost:8091")
    CB_USERNAME = os.environ.get("CB_USERNAME", "Administrator")
    CB_PASSWORD = os.environ.get("CB_PASSWORD", "password")
    
config = {
    "default": "config.BaseConfig"
}

def configure_app(application):
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    application.config.from_object(config[config_name])
    application.config.from_pyfile('config.py', silent=True)
    # Configure logging
    handler = logging.FileHandler(application.config['LOGGING_LOCATION'])
    handler.setLevel(application.config['LOGGING_LEVEL'])
    formatter = logging.Formatter(application.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    application.logger.addHandler(handler)
