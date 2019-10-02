from flask import Response, make_response, Request, request, session
from application import application
import main
import main_ts

@application.route('/metrics', methods=['GET'])
@application.route('/', methods=['GET', 'POST'])
def metrics():
    if request.args.get("timestamp") == "false":
        _value = main.get_metrics(
            application.config['CB_DATABASE'],
            application.config['CB_USERNAME'],
            application.config['CB_PASSWORD'])
        return Response(_value, mimetype='text/plain')
    else:
        _value = main_ts.get_metrics(
            application.config['CB_DATABASE'],
            application.config['CB_USERNAME'],
            application.config['CB_PASSWORD'])
        return Response(_value, mimetype='text/plain')

