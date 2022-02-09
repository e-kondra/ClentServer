import json
import sys
import logging
from datetime import time
from socket import socket, AF_INET, SOCK_STREAM
import time
from select import select

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, \
    MESSAGE_TEXT, MESSAGE, SENDER, DESTINATION, EXIT
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
def clients_message_handling(msg, message_list, client, clients, names):
    # 1.Сообщение о присутствии
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg:
        if msg[USER][ACCOUNT_NAME] not in names.keys():
            names[msg[USER][ACCOUNT_NAME]] = client
            LOG.info('Проверка сообщения в clients_message_handling успешна, ответ: 200')
            send_message(client, {RESPONSE: 200})
        else:
            LOG.warning('Проверка сообщения в check_message не успешна, ответ: Имя пользователя уже занято ')
            send_message(client, {RESPONSE: 400, ERROR: 'Имя пользователя уже занято'})
            clients.remove(client)
            client.close()

    elif ACTION in msg and msg[ACTION] == MESSAGE and TIME in msg and DESTINATION in msg \
            and SENDER in msg and MESSAGE_TEXT in msg:
        LOG.info('Получено сообщение в clients_message_handling, проверка успешна')
        message_list.append(msg)
        return
    elif ACTION in msg and msg[ACTION] == EXIT and ACCOUNT_NAME in msg:
        clients.remove(names[msg[ACCOUNT_NAME]])
        names[msg[ACCOUNT_NAME]].close()
        del names[msg[ACCOUNT_NAME]]
        return
    else:
        LOG.warning('Проверка сообщения в check_message не успешна, ответ: Запрос не корректен ')
        send_message(client,  {RESPONSE: 400, ERROR: 'Запрос не корректен'})
        return


def message_handling(msg, names, clients_wr):
    # msg[DESTINATION] - имя
    # names[message[DESTINATION]] - получатель

    if msg[DESTINATION] in names and names[msg[DESTINATION]] in clients_wr:
        send_message(names[msg[DESTINATION]], msg)
        LOG.info(f'Пользователю {msg[DESTINATION]} отправлено сообщение от {msg[SENDER]}')
    elif msg[DESTINATION] in names and names[msg[DESTINATION]] not in clients_wr:
        raise ConnectionError
    else:
        LOG.error(f'Пользователь {msg[DESTINATION]} не зарегистрирован, отправка сообщения невозможна')


def main():
    listen_address, listen_port = args_parser()
    # create servers socket

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((listen_address, listen_port, ))
    server_socket.settimeout(0.8)

    clients = []
    message_list = []

    # Словарь, содержащий имена пользователей и соответствующие им сокеты.
    names = dict()

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
                    clients_message_handling(clients_message, message_list, client, clients, names)

                except Exception:
                    LOG.info(f'Клиент {client.getpeername()} отключился от сервера.')
                    clients.remove(client)
        # если сообщения для отправки есть , обрабатываем их
        if message_list:
            for i in message_list:
                try:
                    message_handling(i, names, clients_write)
                except Exception:
                    LOG.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            message_list.clear()



if __name__ == '__main__':
    main()

