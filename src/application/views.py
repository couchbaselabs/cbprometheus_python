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

@application.route('/metrics/buckets', methods=['GET'])
@application.route('/buckets', methods=['GET'])
def buckets():
    _value = main.get_buckets(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/query', methods=['GET'])
@application.route('/query', methods=['GET'])
def query():
    _value = main.get_query(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/indexes', methods=['GET'])
@application.route('/indexes', methods=['GET'])
def indexes():
    _value = main.get_indexes(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/eventing', methods=['GET'])
@application.route('/eventing', methods=['GET'])
def eventing():
    _value = main.get_eventing(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/xdcr', methods=['GET'])
@application.route('/xdcr', methods=['GET'])
def xdcr():
    _value = main.get_xdcr(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/analytics', methods=['GET'])
@application.route('/analytics', methods=['GET'])
def analytics():
    _value = main.get_cbas(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/fts', methods=['GET'])
@application.route('/fts', methods=['GET'])
def fts():
    _value = main.get_fts(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/system', methods=['GET'])
@application.route('/system', methods=['GET'])
def system():
    _value = main.get_system(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'])
    return Response(_value, mimetype='text/plain')
