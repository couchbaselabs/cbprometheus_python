from cb_utilities import *
from datetime import datetime

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "exporter"
        self.filters = []
        self.comment = '''This is the method used to access the exporter metrics'''
        self.service_identifier = None
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['nodeList']"},
                        {"value":"cluster_values['clusterName']"}]
        self.exclude = False


def run(url="", user="", passwrd=""):
    exporter_metrics = get_metrics()
    metrics = exporter_metrics['metrics']
    return metrics

def get_metrics():
    '''Exporter metrics'''
    exporter_metrics = {}
    exporter_metrics['metrics'] = []
    sha = ""
    try:
        # This is the best way to get the hash for the repository but it assumes
        # GitPython is installed
        import git
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
    except:
        # This is an alternate way to get the hash for the repository but
        # using subprocess is often considered unsafe, should only be used as a
        # fallback
        import subprocess
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
    exporter_metrics['metrics'].append(
        "{} {{type=\"exporter\", id=\"{}\"}} 1 {}".format(
            "commitID",
            sha,
            get_dt()))

    return exporter_metrics
