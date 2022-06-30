from multiprocessing import cpu_count
from os import environ

bind = '0.0.0.0:' + environ.get('PORT', '8000')
max_requests = 1000
workers = cpu_count()

reload = True
name = 'database'
