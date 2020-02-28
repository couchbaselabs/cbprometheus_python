from cb_utilities import *
import cb_cluster
import re

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "node_exporter"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]}]
        self.comment = '''This is the method used to access prometheus provided Node Exporter Metrics'''
        self.service_identifier = False

def run(url="", user="", passwrd="", nodes=[]):
    '''Entry point for getting the metrics for the analytics nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:
        if len(cluster_values['nodeList']) > 0:
            __metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['nodeList'],
                cluster_values['clusterName'])
            metrics = __metrics['metrics']
    else:
        __metrics = _get_metrics(
            user,
            passwrd,
            nodes,
            cluster_values['clusterName'])
        metrics = __metrics['metrics']

    for metric in metrics:
        print(metric)
    return metrics

def _create_metric(tag, label="", value=""):
    if "#" in tag:
        return(tag.strip())
    else:
     return "{} {{{}}} {}".format(tag, ",".join(label), value)

def _get_metrics(user, passwrd, node_list, cluster_name=""):
    '''Node Exporter Metrics'''
    node_metrics = {}
    node_metrics['metrics'] = []
    node_list.append(get_local_ip())
    auth = basic_authorization(user, passwrd)

    for node in node_list:
        try:
            _ne_url = "http://{}:9200/metrics".format(
                node.split(":")[0])
            a_json = text_request(_ne_url)
            _node = node
            for record in a_json:
                tag = ""
                label = ['\"cluster\":\"{}\"'.format(cluster_name),
                            '\"node\":\"{}\"'.format(_node),
                            '\"type\"=\"node_exporter\"']
                _value = ""
                if len(record) == 0:
                    next
                elif "{" in record:
                    _label = (re.search('\{(.*)\}', record.strip()).group(1)).split(",")
                    label += _label
                    tag = re.search('(.*)\{', record.strip()).group(1)
                    _value = re.search('\}(.*)', record.strip()).group(1)
                    node_metrics['metrics'].append(_create_metric(tag, label, _value))
                elif "#" in record:
                    node_metrics['metrics'].append(_create_metric(record))
                else:
                    tag, _value = record.strip().split(" ")
                    node_metrics['metrics'].append(_create_metric(tag, label, _value))
        except Exception as e:
            print("analytics base: " + str(e))
    return node_metrics
