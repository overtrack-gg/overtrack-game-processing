import hashlib
import os
import logging.config
import socket
import sys
import types


def config_logger(name: str, use_datadog=False, use_stackdriver=False):
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger()

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '[%(asctime)16s | %(levelname)8s | %(name)8s | %(filename)s:%(lineno)s %(funcName)s() ] %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'logs/{name}.log',
                'maxBytes': 1024 * 1024 * 100,
                'backupCount': 3,
                'delay': True
            },
            'file_debug': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'logs/{name}.debug.log',
                'maxBytes': 1024 * 1024 * 100,
                'backupCount': 3,
                'delay': True
            },
            'cherrypy_access': {
                'level': 'DEBUG',
                'formatter': '',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/access.log',
                'maxBytes': 1024,
                'backupCount': 0,
                'delay': True
            }
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file', 'file_debug'],
                'level': 'DEBUG',
                'propagate': True
            },
            'cherrypy.access': {
                'handlers': ['cherrypy_access'],
                'level': 'WARN',
                'propagate': False
            },
            'datadog.api': {
                'handlers': [],
                'level': 'ERROR',
                'propagate': False
            }
        }
    })

    if use_stackdriver:
        import google.cloud.logging
        client = google.cloud.logging.Client()
        client.setup_logging()

    if use_datadog:
        import datadog
        from datadog_logger import DatadogLogHandler
        datadog.initialize(api_key=os.environ['DATADOG_API_KEY'], app_key=os.environ['DATADOG_APP_KEY'])
        datadog_handler = DatadogLogHandler(tags=[f'host:{socket.gethostname()}', f'pid:{os.getpid()}', f'stack:{name}', 'type:log'], mentions=[], level=logging.INFO)
        logger.addHandler(datadog_handler)

    for _ in range(3):
        logger.info('')
    logger.info(f'Command: "{" ".join(sys.argv)}", pid={os.getpid()}, name={name}')

    hsh = hashlib.md5()
    modules = [
        m.__file__ for m in globals().values() if
        isinstance(m, types.ModuleType) and
        hasattr(m, '__file__')
    ]
    modules.append(__file__)
    for mod in sorted(modules):
        print(mod)
        with open(mod, 'rb') as f:
            hsh.update(f.read())
    logger.info(f'Modules hash: {hsh.hexdigest()}')
