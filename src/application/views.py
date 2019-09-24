from flask import Response, make_response, Request, request, session
from flask import render_template, flash, redirect, url_for
from application import application
from main import *

import json
import main

########################This starts the page renders#######################################

@application.route('/metrics', methods=['GET', 'POST'])
@application.route('/', methods=['GET', 'POST'])
def index():
    _value = main.get_metrics(application.config['CB_DATABASE'], application.config['CB_USERNAME'], application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')
