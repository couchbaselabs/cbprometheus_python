from flask import Response, make_response, Request, request, session
from application import application
import main
import main_ts
import json

########################This starts the page renders#######################################

@application.route('/metrics', methods=['GET', 'POST'])
@application.route('/', methods=['GET', 'POST'])
def metrics():
    _value = main.get_metrics(application.config['CB_DATABASE'], application.config['CB_USERNAME'], application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

@application.route('/metrics_ts', methods=['GET', 'POST'])
def metrics_ts():
    _value = main_ts.get_metrics(application.config['CB_DATABASE'], application.config['CB_USERNAME'], application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')