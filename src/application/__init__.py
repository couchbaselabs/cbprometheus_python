from flask import Flask
from config import configure_app

application = Flask(__name__)

configure_app(application)

@application.errorhandler(500)
def internal_server_error(error):
    application.logger.error('Server Error: %s', (error))
    error = 'Server Error: %s', (error)
    return 'Server Error:'

#@application.errorhandler(Exception)
#def unhandled_exception(error):
#    application.logger.error('Unhandled Exception: %s', (error))
#    error = 'Unhandled Exception: %s', (error)
#    return 'Server Error:'

if __name__ == 'application':
    from application import views
