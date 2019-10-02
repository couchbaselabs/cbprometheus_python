from flask import Response, make_response, Request, request, session
from application import application
import main
import main_ts
import json

########################This starts the page renders######################


@application.route('/metrics', methods=['GET'])
@application.route('/', methods=['GET', 'POST'])
def metrics():
    if request.args.get("timestamp").lower() == "false":
        print("No Timestamp")
        _value = main.get_metrics(
            application.config['CB_DATABASE'],
            application.config['CB_USERNAME'],
            application.config['CB_PASSWORD'])
        return Response(_value, mimetype='text/plain')
    else:
        print("Yes Timestamp")
        _value = main_ts.get_metrics(
            application.config['CB_DATABASE'],
            application.config['CB_USERNAME'],
            application.config['CB_PASSWORD'])
        return Response(_value, mimetype='text/plain')

