import sys
import time
from socket import *
import json
import logging
import logs.configs.client_log_config

from common.variables import *
from common.utils import send_message, get_message

LOG = logging.getLogger('client')

def get_answer(msg):
    '''get answer from server'''
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            return '200 : OK'
        LOG.debug('Получен ответ 400')
        return f'400 : {msg[ERROR]}'
    raise ValueError


def make_presence(account_name='Guest'):
    '''generate clients presence request'''
    request = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return request


def main():
    '''Load common line options'''
    # client.py 78.56.51.221 8888
    try:
        server_address = sys.argv[2]
        server_port = int(sys.argv[3])
        LOG.info(f'Подключение к {server_address} {server_port}')
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        LOG.warning(f'Внимание! невозможно определить порт или адрес сервера. Используются данные по умолчанию {DEFAULT_IP_ADDRESS} {DEFAULT_PORT}')
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        LOG.critical(f'Ошибка! Клиент с портом {server_port}. В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)
    # create socket and make connection
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((server_address, server_port))
    except Exception as err:
        LOG.critical(f'Подключение не установлено. Причина {err}')
    # make and send presence-message (say hello to server)
    msg = make_presence()
    send_message(client_socket, msg)
    # get an answer from server
    try:
        answer = get_answer(get_message(client_socket))
        LOG.debug(f'Получен ответ {answer}')
    except (ValueError, json.JSONDecodeError):
        LOG.error('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
