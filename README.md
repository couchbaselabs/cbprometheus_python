# cbstats

set environment variables:<br/>

```
export CB_DATABASE='<>' 
export CB_USERNAME='<>'
export CB_PASSWORD='<>'
```

run with uwsgi<br/>
uwsgi --http :5000 --processes 5 --pidfile /tmp/cbstats.pid --master --wsgi-file wsgi.py

### To Run with Docker:

```
docker network create -d macvlan --subnet=<>/<> --gateway=<> -o parent=enp2s0 --ip-range <>/<> pub_net
cd <gitRepo>
docker build --tag=cbstats .
docker run --name <container name> --env CB_DATABASE='<cluster address' --env CB_USERNAME='<username>' --env CB_PASSWORD='<password>' --network=pub_net cbstats
docker start <container name>
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container name>
```

