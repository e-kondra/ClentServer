import json
import sys
import logging
from datetime import time
from socket import socket, AF_INET, SOCK_STREAM
import time
from select import select

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, \
    MESSAGE_TEXT, MESSAGE, SENDER
from common.utils import get_message, send_message
from logs.configs import server_log_config
from decors import log

LOG = logging.getLogger('server')


@log
def args_parser():
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
    return  listen_address, listen_port


@log
def clients_message_handling(msg, message_list, client):
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
        LOG.info('Проверка сообщения в clients_message_handling успешна, ответ: 200')
        send_message(client, {RESPONSE: 200})
    elif ACTION in msg and msg[ACTION] == MESSAGE and TIME in msg and MESSAGE_TEXT in msg:
        LOG.info('Получено сообщение в clients_message_handling, проверка успешна')
        message_list.append((msg[ACCOUNT_NAME], msg[MESSAGE_TEXT]))
        return
    else:
        LOG.warning('Проверка сообщения в check_message не успешна, ответ: Bad request ')
        send_message(client,  {RESPONSE: 400, ERROR: 'Bad request'})


def main():
    listen_address, listen_port = args_parser()
    # create servers socket

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((listen_address, listen_port, ))
    server_socket.settimeout(0.8)

    clients = []
    message_list = []

    server_socket.listen(MAX_CONNECTIONS)
    # endless cycle to waiting clients
    while True:
        # connecting
        try:
            client_socket, client_addr = server_socket.accept()
        except OSError:
            pass
        else:
            LOG.info(f'Соединение установлено c {client_addr}')
            clients.append(client_socket)

        clients_read = []
        clients_write = []
        clients_exc = []

        try:
            if clients:
                clients_read, clients_write, clients_exc = select(clients, clients, [], 0)
        except OSError:
            pass

        if clients_read:
            for client in clients_read:
                try:
                    clients_message = get_message(client)
                    LOG.info(f'Получено сообщение {clients_message}')
                    clients_message_handling(clients_message, message_list, client)

                except:
                    LOG.info(f'Клиент {client.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client)
        # если сообщения для отправки есть и клиенты есть, то
        if message_list:
            if clients_write:
                # формируем сообщение
                message = {
                    ACTION: MESSAGE,
                    SENDER: message_list[0][0],
                    TIME: time.time(),
                    MESSAGE_TEXT: message_list[0][1]
                }
                del message_list[0]
                #  отправляем сообщение на всех клиентов из списка
                for client in clients_write:
                    try:
                        send_message(client, message)
                    except Exception as err:
                        LOG.info(f'Клиент {client.getpeername()} отключился от сервера.{err}')
                        clients.remove(client)


if __name__ == '__main__':
    main()

