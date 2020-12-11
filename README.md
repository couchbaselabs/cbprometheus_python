# Couchbase Prometheus Exporter

### To run Locally

Install requirements<br />

```
# pip install -r requirements
```

set environment variables:<br/>

```
export CB_DATABASE='<>,<>'
export CB_USERNAME='<>'
export CB_PASSWORD='<>'
```

Please list more than one node in the list of nodes. It does not matter the order or the service running on the node. The nodes must be separated by commas.

By default the exporter runs in a "cluster" configuration, this way when it is scraped it will return all of the relevant metrics for a particular service for each node in the cluster.  This way only a single exporter has to be configured per cluster, however this may be undesirable or you may wish to install the exporter on each node in the cluster to reduce the overall payload size of metrics returned.  To do this set the variable `CB_EXPORTER_MODE` to local, then all requests will only be made to the localhost, and only relevant metrics to that single node will be returned. 

```bash
export CB_EXPORTER_MODE="local"
```

if you are working with very large clusters or clusters with many indexes it may be more performant to stream your results to prometheus instead of trying to load the full dataset at one time. To do that export the following variable</br>

```
export CB_STREAMING=true
```

Another way to lower the payload size is to reduce the number of samples per poll. You can do this by saying how many samples you want from the last 1 minute. Valid entries are: 1,2,3,4,5,6,10,12,15,20,30,60. You can enter other values but if they are not valid the system will get as close as possible to your number.
```
export  CB_RESULTSET=1
```

If you would like to run cbstats from the exporter to load into prometheus and grafana you need to set up passwordless ssh using an ssh key. Once the public key is loaded on each of the couchbase nodes and the private key loaded on the exporter you can then configure the exporter to use the key. The user will need to have access to run cbstats in whatever directory you have installed it. By default that will be /opt/couchbase/bin/cbstats

```
export CB_KEY=/path/to/private/key
export CB_CBSTAT_PATH = /opt/couchbase/bin/cbstats
export CB_SSH_UN = username associated with key
```

If you are not using docker to run this it may be beneficial to create and add these variables to the /etc/profile.d/exporter.sh
```
sudo su
{
    echo 'export CB_DATABASE="<>,<>"'
    echo 'export CB_USERNAME="<>"'
    echo 'export CB_PASSWORD="<>"'
    echo 'export CB_KEY=/path/to/private/key'
    echo 'export CB_CBSTAT_PATH = /opt/couchbase/bin/cbstats'
    echo 'export CB_SSH_UN = username associated with key'
} > /etc/profile.d/exporter.sh
sudo chmod +x /etc/profile.d/exporter.sh
source /etc/profile.d/exporter.sh
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
