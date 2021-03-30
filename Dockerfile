FROM centos:centos7

WORKDIR /opt

RUN yum -y update && \
    yum -y install epel-release && \
    yum -y install git && \
    yum -y install python-devel && \
    yum -y install python-pip && \
    yum -y install gcc && \
    yum -y install wget

RUN git clone https://github.com/couchbaselabs/cbprometheus_python.git

RUN pip install -r /opt/cbprometheus_python/requirements

WORKDIR /opt/cbprometheus_python/src

EXPOSE 5000

ENV CB_DATABASE = localhost
ENV CB_USERNAME = Administrator
ENV CB_PASSWORD = password
ENV CB_STREAMING = true
ENV CB_RESULTSET = 60
ENV CB_EXPORTER_MODE = cluster
ENV CB_NODE_EXPORTER_PORT = 9200
ENV CB_PROCESS_EXPORTER_PORT = 9256
ENV CB_EXPORTER_TIMEOUT = 5

CMD ["uwsgi", "--http", ":5000", "--processes", "5", "--pidfile", "/tmp/cbstats.pid", "--master", "--wsgi-file", "wsgi.py"]
