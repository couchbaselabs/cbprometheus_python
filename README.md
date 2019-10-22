# Couchbase Prometheus Exporter

### To run Locally

Install requirements<br />

```
# pip install -r requirements
```

set environment variables:<br/>

```
export CB_DATABASE='<>' 
export CB_USERNAME='<>'
export CB_PASSWORD='<>'
```

if you are working with very large clusters or clusters with many indexes it may be more performant to stream your results to prometheus instead of trying to load the full dataset at one time. To do that export the following variable</br>
```
export CB_STREAMING=true
```

run with uwsgi<br/>
```
uwsgi --http :5000 --processes 5 --pidfile /tmp/cbstats.pid --master --wsgi-file wsgi.py
```

### To Run with Docker:

```
# docker network create -d macvlan --subnet=<>/<> --gateway=<> -o parent=<> --ip-range=<>/<> pub_net
# cd <gitRepo>
# docker build --tag=cbstats .
# docker run --name <container name> --env CB_DATABASE='<cluster address>' --env CB_USERNAME='<username>' --env CB_PASSWORD='<password>' --env CB_STREAMING=true --network pub_net cbstats
# docker start <container name>
# docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container name>
```

### Prometheus Configuration
To configure Prometheus a config file has been added to this repositiory utilizing the different endpoints available in this exporter.

### To Run Prometheus with Docker
```
$ cd <gitRepo>/prometheus .
# docker build -t my-prometheus .
# docker run --name <container name> -p 9090:9090 --network pub_net my-prometheus
ctrl+c
# docker start <container name>
# docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container name>
```

### To run Grafana with Docker
```
# docker run -d -p 3000:3000 --name <container name> --network pub_net -e "GF_INSTALL_PLUGINS=grafana-clock-panel,camptocamp-prometheus-alertmanager-datasource" grafana/grafana
# docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container name>
```

### Testing
With the exporter running an easy way to test if you have connectivity is to use your browser or curl to test the endpoints<br />

```curl http://<ipaddress>:5000/metrics/system```

To test that the metrics are being returned in the way Prometheus expects to read them you can use the promtool. The following command must be run from the Prometheus installation directory.<br />

```curl -s http://<ipaddress>:5000/metrics/system | ./promtool check metrics``` 
