from cb_utilities import *
from datetime import datetime

def _get_exporter_metrics():
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
