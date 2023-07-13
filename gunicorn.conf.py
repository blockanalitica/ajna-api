bind = ":8000"
workers = 2
threads = 4
worker_class = "gthread"
wsgi_app = "config.wsgi:application"
max_requests = 100000
timeout = 60
worker_tmp_dir = "/dev/shm"
