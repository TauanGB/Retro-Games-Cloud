# Configuração do Gunicorn para Retro Games Cloud

import multiprocessing
import os

# Bind address
bind = "0.0.0.0:8000"

# Workers
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# Process naming
proc_name = "retro_games_cloud"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (se necessário)
# keyfile = None
# certfile = None

# Performance
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Graceful timeout
graceful_timeout = 30

# Worker timeout
worker_tmp_dir = "/dev/shm"






