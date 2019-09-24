# cbstats

set environment variables:<br/>
```export CB_DATABASE='<>' 
export CB_USERNAME='<>'
export CB_PASSWORD='<>'
```

run with uwsgi<br/>
uwsgi --http :5000 --processes 5 --pidfile /tmp/cbstats.pid --master --wsgi-file wsgi.py
