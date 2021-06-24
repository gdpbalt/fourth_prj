import multiprocessing
from tempfile import mkdtemp

bind = 'localhost:8000'
workers = 3
max_requests = 1000

#syslog_addr = 'udp://10.0.0.188:514'
syslog = False

# accesslog - The Access log file to write to.
# “-” means log to stdout.
accesslog = None
errorlog = "/var/log/flask/error.log"
