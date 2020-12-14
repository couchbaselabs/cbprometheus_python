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
    CB_DATABASE = os.environ.get("CB_DATABASE", "localhost")
    CB_USERNAME = os.environ.get("CB_USERNAME", "Administrator")
    CB_PASSWORD = os.environ.get("CB_PASSWORD", "password")
    CB_STREAMING = os.environ.get("CB_STREAMING")
    CB_RESULTSET = os.environ.get("CB_RESULTSET")
    CB_CBSTAT_PATH = os.environ.get("CB_CBSTAT_PATH")
    CB_MCTIMING_PATH = os.environ.get("CB_MCTIMING_PATH")
    CB_KEY = os.environ.get("CB_KEY")
    CB_SSH_UN = os.environ.get("CB_SSH_USER")
    CB_SSH_HOST = os.environ.get("CB_SSH_HOST")
    CB_EXPORTER_MODE = os.environ.get("CB_EXPORTER_MODE", "cluster")
    CB_NODE_EXPORTER_PORT = os.environ.get("CB_NODE_EXPORTER_PORT", "9200")
    CB_PROCESS_EXPORTER_PORT = os.environ.get("CB_PROCESS_EXPORTER_PORT", "9256")

    # if the exporter is being ran in local mode, i.e. on each couchbase node,
    # override the CB_DATABASE value to be localhost so that all requests will be
    # to the local machine
    if CB_EXPORTER_MODE == "local":
      CB_DATABASE = "localhost"

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
