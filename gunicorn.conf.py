import os

# Sensible production defaults for this project
workers = int(os.getenv("GUNICORN_WORKERS", "4"))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
threads = int(os.getenv("GUNICORN_THREADS", "4"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")
accesslog = "-"
errorlog = "-"
capture_output = True
