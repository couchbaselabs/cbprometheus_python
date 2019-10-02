from flask import Response, make_response, Request, request, session
from application import application
import main

@application.route('/metrics', methods=['GET'])
@application.route('/', methods=['GET', 'POST'])
def metrics():
    _value = main.get_metrics(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

