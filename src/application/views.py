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

@application.route('/metrics/system', methods=['GET'])
@application.route('/system', methods=['GET'])
def system():
    node_list = []
    if request.args.get("nodes"):
        node_str = request.args.get("nodes")
        node_str = node_str.replace("[", "").replace("]", "").replace(" ", "").replace(":8091", "")
        node_list = node_str.split(",")
    _value = main.get_system(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'],
        node_list)
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/buckets', methods=['GET'])
@application.route('/buckets', methods=['GET'])
def buckets():
    node_list = []
    if request.args.get("nodes"):
        node_str = request.args.get("nodes")
        node_str = node_str.replace("[", "").replace("]", "").replace(" ", "").replace(":8091", "")
        node_list = node_str.split(",")

    bucket_list = []
    if request.args.get("buckets"):
        bucket_str = request.args.get("buckets")
        bucket_str = bucket_str.replace("[", "").replace("]", "").replace(" ", "")
        bucket_list = bucket_str.split(",")

    _value = main.get_buckets(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'],
        bucket_list,
        node_list)

    return Response(_value, mimetype='text/plain')

@application.route('/metrics/query', methods=['GET'])
@application.route('/query', methods=['GET'])
def query():
    node_list = []
    if request.args.get("nodes"):
        node_str = request.args.get("nodes")
        node_str = node_str.replace("[", "").replace("]", "").replace(" ", "").replace(":8091", "")
        node_list = node_str.split(",")

    _value = main.get_query(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'],
        node_list)
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/indexes', methods=['GET'])
@application.route('/indexes', methods=['GET'])
def indexes():
    node_list = []
    if request.args.get("nodes"):
        node_str = request.args.get("nodes")
        node_str = node_str.replace("[", "").replace("]", "").replace(" ", "").replace(":8091", "")
        node_list = node_str.split(",")

    bucket_list = []
    if request.args.get("buckets"):
        bucket_str = request.args.get("buckets")
        bucket_str = bucket_str.replace("[", "").replace("]", "").replace(" ", "")
        bucket_list = bucket_str.split(",")

    index_list = []
    if request.args.get("index"):
        index_str = request.args.get("index")
        index_str = index_str.replace("[", "").replace("]", "").replace(" ", "")
        index_list = index_str.split(",")

    _value = main.get_indexes(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'],
        index_list,
        bucket_list,
        node_list)
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/eventing', methods=['GET'])
@application.route('/eventing', methods=['GET'])
def eventing():
    node_list = []
    if request.args.get("nodes"):
        node_str = request.args.get("nodes")
        node_str = node_str.replace("[", "").replace("]", "").replace(" ", "").replace(":8091", "")
        node_list = node_str.split(",")

    _value = main.get_eventing(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'],
        node_list)
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/xdcr', methods=['GET'])
@application.route('/xdcr', methods=['GET'])
def xdcr():
    node_list = []
    if request.args.get("nodes"):
        node_str = request.args.get("nodes")
        node_str = node_str.replace("[", "").replace("]", "").replace(" ", "").replace(":8091", "")
        node_list = node_str.split(",")

    bucket_list = []
    if request.args.get("buckets"):
        bucket_str = request.args.get("buckets")
        bucket_str = bucket_str.replace("[", "").replace("]", "").replace(" ", "")
        bucket_list = bucket_str.split(",")

    _value = main.get_xdcr(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'],
        node_list,
        bucket_list)
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/analytics', methods=['GET'])
@application.route('/analytics', methods=['GET'])
def analytics():
    node_list = []
    if request.args.get("nodes"):
        node_str = request.args.get("nodes")
        node_str = node_str.replace("[", "").replace("]", "").replace(" ", "").replace(":8091", "")
        node_list = node_str.split(",")

    _value = main.get_cbas(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'],
        node_list)
    return Response(_value, mimetype='text/plain')

@application.route('/metrics/fts', methods=['GET'])
@application.route('/fts', methods=['GET'])
def fts():
    node_list = []
    if request.args.get("nodes"):
        node_str = request.args.get("nodes")
        node_str = node_str.replace("[", "").replace("]", "").replace(" ", "").replace(":8091", "")
        node_list = node_str.split(",")

    bucket_list = []
    if request.args.get("buckets"):
        bucket_str = request.args.get("buckets")
        bucket_str = bucket_str.replace("[", "").replace("]", "").replace(" ", "")
        bucket_list = bucket_str.split(",")

    _value = main.get_fts(
        application.config['CB_DATABASE'],
        application.config['CB_USERNAME'],
        application.config['CB_PASSWORD'],
        node_list,
        bucket_list)
    return Response(_value, mimetype='text/plain')


