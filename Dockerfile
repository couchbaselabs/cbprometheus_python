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

RUN pip install --upgrade pip && \
    pip install -r /opt/cbprometheus_python/src/requirements

WORKDIR /opt/cbprometheus_python/src

EXPOSE 5000

ENV CB_DATABASE 192.168.1.19
ENV CB_USERNAME Administrator
ENV CB_PASSWORD password

CMD ["uwsgi", "--http", ":5000", "--processes", "5", "--pidfile", "/tmp/cbstats.pid", "--master", "--wsgi-file", "wsgi.py"]
