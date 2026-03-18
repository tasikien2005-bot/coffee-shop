"""Gunicorn configuration for Docker deployment"""

# Server socket
bind = "0.0.0.0:5000"

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
threads = 2

# Timeout
timeout = 120
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "coffee_shop"

# Server mechanics
preload_app = True
max_requests = 1000
max_requests_jitter = 50