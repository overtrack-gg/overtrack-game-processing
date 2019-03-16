import logging
import multiprocessing
import os
import re
import socket
import time
from typing import Optional

logger = logging.getLogger(__name__)

HOST = 'irc.chat.twitch.tv'
PORT = 6667
NICK = os.environ.get('TWITCH_BOT_USERNAME', 'OverTrackGG')
PASS = os.environ['TWITCH_OAUTH_TOKEN']


def _send_privmessage(channel: str, message: str, colour: Optional[str] = None) -> None:
    s = socket.socket()
    print(f'* Connecting to {HOST}:{PORT}')
    s.connect((HOST, PORT))
    print('* Connection established')

    def send(command: str) -> None:
        time.sleep(0.1)
        command += '\r\n'
        safe_print_command = re.sub('oauth:\w+', 'oauth:****', command)
        print(f'> {repr(safe_print_command)}')
        s.send(command.encode('utf-8'))

    send(f'PASS oauth:{PASS}')
    send(f'NICK {NICK}')

    if colour:
        send(f'PRIVMSG #{channel } :.color {colour}')
        send(f'PRIVMSG #{channel } :/me {message}')
    else:
        send(f'PRIVMSG #{channel } :{message}')

    response = s.recv(1024)
    for line in response.decode('utf-8').split('\n'):
        print('< ' + repr(line + '\n'))

    print('* Closing connection')
    s.close()


def send_message(channel: str, message: str, colour: Optional[str] = None, timeout: int = 10) -> bool:
    logger.info('Sending IRC message to %s #%s: "%s" with timeout %ds', HOST, channel, message, timeout)

    process = multiprocessing.Process(
        target=_send_privmessage,
        args=(channel, message),
        kwargs={'colour': colour},
    )
    logger.info('Starting process')
    start = time.time()
    process.start()
    process.join()
    if process.is_alive():
        logger.error('IRC process did not complete in %ds - terminating', timeout)
        process.terminate()
        logger.warning('Process terminated')

    logger.info('Process completed with exitcode %s in %1.1fs', process.exitcode, time.time() - start)
    return process.exitcode == 0


if __name__ == '__main__':
    from overtrack.util.logging_config import config_logger
    config_logger('twitch_bot', logging.DEBUG, False)
    send_message('eeveea_', 'Hello in there?', colour='OrangeRed')
