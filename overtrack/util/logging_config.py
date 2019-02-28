import inspect
import logging
import logging.config
import os
import socket
import sys
import time
from collections import defaultdict
from threading import Thread
from typing import Callable, Optional, Sequence, Mapping

LOG_FORMAT = '[%(asctime)16s | %(levelname)8s | %(name)24s | %(filename)s:%(lineno)s %(funcName)s() ] %(message)s'


def intermittent_log(
        logger: logging.Logger,
        line: str, frequency: float=60,
        level=logging.INFO,
        negative_level: Optional[int]=None,
        _last_logged=defaultdict(float)):
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
    except BaseException:
        # noinspection PyProtectedMember
        logger._log(level, line, ())


upload_logs_settings = {
    'write_to_file': False,
    'upload_func': lambda s1, s2: None,
    'args': ()
}


def config_logger(
        name: str,
        level: int=logging.INFO,

        write_to_file=True,

        use_datadog=False,
        use_stackdriver=False,

        stackdriver_level=logging.INFO,

        use_stackdriver_error=False,

        upload_func: Optional[Callable[[str, str], None]]=None,
        upload_frequency: Optional[float]=None):

    logger = logging.getLogger()

    handlers = {
        'default': {
            'level': logging.getLevelName(level),
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        }
    }
    if write_to_file:
        os.makedirs('logs', exist_ok=True)
        handlers.update({
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
        })
    else:
        handlers.update({
            'file': {
                'class': 'logging.NullHandler',
            },
            'file_debug': {
                'class': 'logging.NullHandler',
            },
            'web_access': {
                'class': 'logging.NullHandler',
            }
        })

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': LOG_FORMAT
            },
        },
        'handlers': handlers,
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
            'libav.swscaler': {
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
        from google.cloud.logging.handlers import CloudLoggingHandler
        from google.cloud.logging.handlers.handlers import EXCLUDED_LOGGER_DEFAULTS

        # noinspection PyUnresolvedReferences
        client = google.cloud.logging.Client()
        # client.setup_logging()

        handler = CloudLoggingHandler(client, name=name)
        handler.setLevel(stackdriver_level)
        logger.addHandler(handler)
        for logger_name in EXCLUDED_LOGGER_DEFAULTS + ('urllib3.connectionpool', ):
            exclude = logging.getLogger(logger_name)
            exclude.propagate = False
            # exclude.addHandler(logging.StreamHandler())

    if use_stackdriver_error:
        from google.cloud import error_reporting
        client = error_reporting.Client()

    if use_datadog:
        import datadog
        from datadog_logger import DatadogLogHandler
        datadog.initialize(api_key=os.environ['DATADOG_API_KEY'], app_key=os.environ['DATADOG_APP_KEY'])
        datadog_handler = DatadogLogHandler(
            tags=[
                f'host:{socket.gethostname()}',
                f'pid:{os.getpid()}',
                f'stack:{name}',
                'type:log'],
            mentions=[],
            level=logging.INFO
        )
        logger.addHandler(datadog_handler)

    for _ in range(3):
        logger.info('')
    logger.info(f'Command: "{" ".join(sys.argv)}", pid={os.getpid()}, name={name}')
    if use_stackdriver:
        logger.info(f'Connected to google cloud logging. Using name="{name}". Logging class: {logging.getLoggerClass()}')

    upload_logs_settings['write_to_file'] = write_to_file
    if write_to_file and upload_func and upload_frequency:
        upload_logs_settings['upload_func'] = upload_func
        file: str = handlers['file']['filename']
        file_debug: str = handlers['file_debug']['filename']
        # noinspection PyTypeChecker
        upload_logs_settings['args'] = file, file_debug

        def upload_loop():
            while True:
                time.sleep(upload_frequency)
                upload_func(handlers['file']['filename'], handlers['file_debug']['filename'])
        logger.info(f'Uploading log files every {upload_frequency}s')
        Thread(target=upload_loop, daemon=True).start()

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


def finish_logging():
    if upload_logs_settings['write_to_file'] and upload_logs_settings['upload_func']:
        upload_logs_settings['upload_func'](*upload_logs_settings['args'])


def patch_sentry_locals_capture():
    import sentry_sdk.utils
    from overtrack.frame import Frame

    def object_to_json(obj):
        def _walk(obj, depth):
            if depth < 4:
                if isinstance(obj, Frame):
                    return {'timestamp': obj.timestamp}
                if isinstance(obj, list) and len(obj) > 2 and isinstance(obj[0], Frame) and isinstance(obj[-1], Frame):
                    return [_walk(obj[0], depth), f'...<{len(obj)-2}>...', _walk(obj[-1], depth)]
                if isinstance(obj, Sequence) and not isinstance(obj, (bytes, str)):
                    return [_walk(x, depth + 1) for x in obj]
                if isinstance(obj, Mapping):
                    return {sentry_sdk.utils.safe_str(k): _walk(v, depth + 1) for k, v in obj.items()}
            return sentry_sdk.utils.safe_repr(obj)

        return _walk(obj, 0)

    sentry_sdk.utils.object_to_json = object_to_json


def main() -> None:
    config_logger('adasd', level=logging.INFO)
    logger = logging.getLogger()
    logger.info('foo')


if __name__ == '__main__':
    main()