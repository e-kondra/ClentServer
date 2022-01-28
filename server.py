import json
import sys
import logging
from socket import socket, AF_INET, SOCK_STREAM

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS,PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message
from logs.configs import server_log_config

LOG = logging.getLogger('server')

def check_message(msg):
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
        LOG.info('Проверка сообщения в check_message успешна, ответ: 200')
        return {RESPONSE: 200}
    LOG.warning('Проверка сообщения в check_message не успешна, ответ: Bad request ')
    return {RESPONSE: 400, ERROR: 'Bad request'}


def main():
    # server.py -p 8880 -a 192.168.56.1

    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        LOG.critical('Проверка порта: После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        LOG.critical(
            'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        LOG.critical(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)
    # create servers socket

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((listen_address, listen_port, ))

    server_socket.listen(MAX_CONNECTIONS)
    # endless cycle to waiting clients
    while True:
        client_socket, client_addr = server_socket.accept()
        try:
            clients_message = get_message(client_socket)
            LOG.info(f'Получено сообщение {clients_message}')
            response = check_message(clients_message)
            LOG.info(f'Сообщение проверено, сформирован ответ: {response}')
            send_message(client_socket, response)
            LOG.info(f'Ответ отправлен, соединениe с клиентом {client_addr} закрывается')
            client_socket.close()
        except (ValueError, json.JSONDecodeError):
            LOG.error('Принято некорретное сообщение от клиента.')
            client_socket.close()



if __name__ == '__main__':
    main()

