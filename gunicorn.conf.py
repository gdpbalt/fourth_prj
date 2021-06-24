import multiprocessing
from tempfile import mkdtemp

bind = 'localhost:8000'
workers = 5
max_requests = 1000
timeout = 300

#syslog_addr = 'udp://10.0.0.188:514'
#syslog = True

# accesslog - The Access log file to write to.
# “-” means log to stdout.
accesslog = None
#accesslog = "/var/log/flask/access.log"
errorlog = "/var/log/flask/error.log"

