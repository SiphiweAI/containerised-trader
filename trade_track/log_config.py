# import logging
# import sys

# def setup_logging():
#     handler = logging.StreamHandler(sys.stdout)
#     handler.setFormatter(logging.Formatter(
#         '%(asctime)s - %(levelname)s - %(message)s'
#     ))

#     logging.basicConfig(
#         level=logging.INFO,       
#         handlers=[handler]
#     )


import logging
from logging.config import dictConfig

def setup_logging():
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
