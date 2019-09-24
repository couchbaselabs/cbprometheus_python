# cbstats

run with uwsgi<br/>
uwsgi --http :5000 --processes 5 --pidfile /tmp/cbstats.pid --master --wsgi-file wsgi.py
