import inspect
import os
import logging.config
import socket
import sys
import time
from collections import defaultdict
from typing import Union, Optional

LOG_FORMAT = '[%(asctime)16s | %(levelname)8s | %(name)24s | %(filename)s:%(lineno)s %(funcName)s() ] %(message)s'


def intermittent_log(logger: logging.Logger, line: str, frequency: float=60, level=logging.INFO, negative_level: Optional[int]=None, _last_logged=defaultdict(float)):
    try:
        caller = inspect.stack()[1]
        output = negative_level
        frame_id = caller.filename, caller.lineno
        if time.time() - _last_logged[frame_id] > frequency:
            _last_logged[frame_id] = time.time()
            output = level
        if output and logger.isEnabledFor(output):
            co = caller.frame.f_code
            fn, lno, func, sinfo = (co.co_filename, caller.frame.f_lineno, co.co_name, None)
            record = logger.makeRecord(logger.name, output, fn, lno, line, (), None, func, None, sinfo)
            logger.handle(record)
    except Exception:
        logger._log(level, line)


def config_logger(name: str, level: int=logging.INFO, use_datadog=False, use_stackdriver=False):
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger()

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': LOG_FORMAT
            },
        },
        'handlers': {
            'default': {
                'level': logging.getLevelName(level),
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
            'web_access': {
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
                'handlers': ['web_access'],
                'level': 'WARN',
                'propagate': False
            },
            'sanic.access': {
                'handlers': ['web_access'],
                'level': 'WARN',
                'propagate': False
            },
            'libav.AVBSFContext': {
                'handlers': ['default', 'file', 'file_debug'],
                'level': 'CRITICAL',
                'propagate': False
            },
            
            'datadog.api': {
                'handlers': [],
                'level': 'ERROR',
                'propagate': False
            },
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

    # hsh = hashlib.md5()
    # modules = [
    #     m.__file__ for m in globals().values() if
    #     isinstance(m, types.ModuleType) and
    #     hasattr(m, '__file__')
    # ]
    # modules.append(__file__)
    # for mod in sorted(modules):
    #     with open(mod, 'rb') as f:
    #         hsh.update(f.read())
    # logger.info(f'Modules hash: {hsh.hexdigest()}')


def bar():
    logger.debug('bar')
    intermittent_log(logger, 'bar', 5)
    intermittent_log(otherlogger, 'bar', 5)


def foo():
    bar()
    logger.debug('foo')
    intermittent_log(logger, 'foo', 15)
    intermittent_log(logger, 'foo', 10,)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger = logging.getLogger(__name__)
    otherlogger = logging.getLogger('otherlogger')
    logger.info('foo')
    for i in range(1000):
        intermittent_log(otherlogger, f'test {i}', 10)
        foo()
        time.sleep(1)
