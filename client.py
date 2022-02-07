import argparse
import sys
import time
from socket import *
import json
import logging
import logs.configs.client_log_config


from common.variables import *
from common.utils import send_message, get_message
from errors import ReqFieldMissingError, ServerError
from decors import log

LOG = logging.getLogger('client')


@log
def get_answer_presence(msg):
    '''get answer from server'''
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            return '200 : OK'
        LOG.debug('Получен ответ 400')
        return f'400 : {msg[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)

@log
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


@log
def arg_parser():
    '''Load common line options like
    # client.py 78.56.51.221 8888
    and read params and return 3 params: server_address, server_port, client_mode
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default=LISTEN_MODE, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        LOG.critical(
            f'Ошибка! Клиент с портом {server_port}. В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in (LISTEN_MODE, SEND_MODE):
        LOG.critical(f'Указан недопустимый режим работы {client_mode}, '
                     f'допустимые режимы: {LISTEN_MODE} , {SEND_MODE}')
        sys.exit(1)

    return server_address, server_port, client_mode


def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    message = input('Введите сообщение для отправки или \'!\' для завершения работы: ')
    if message == '!':
        sock.close()
        LOG.info('Завершение работы по команде пользователя.')
        sys.exit(0)
    msg = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    LOG.debug(f'Сформирован словарь сообщения: {msg}')
    return msg

@log
def listen_message_from_server(msg):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    LOG. info('listen_message_from_server')
    if ACTION in msg and msg[ACTION] == MESSAGE and SENDER in msg and MESSAGE_TEXT in msg:
        print(f'Получено сообщение от пользователя '
              f'{msg[SENDER]}:\n{msg[MESSAGE_TEXT]}')
        LOG.info(f'Получено сообщение от пользователя '
                    f'{msg[SENDER]}:\n{msg[MESSAGE_TEXT]}')
    else:
        LOG.error(f'Получено некорректное сообщение с сервера: {msg}')



def main():

    """Загружаем параметы коммандной строки"""
    server_address, server_port, client_mode = arg_parser()

    LOG.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, режим работы: {client_mode}')

    # create socket and make connection

    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        # presence
        send_message(client_socket, make_presence())
        answer = get_answer_presence(get_message(client_socket))
        LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        LOG.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        LOG.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        LOG.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        LOG.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:

        while True:
            # режим работы - отправка сообщений
            if client_mode == SEND_MODE:
                LOG.info(f'Режим {SEND_MODE}')
                try:
                    send_message(client_socket, create_message(client_socket))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOG.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)
            # Режим работы приём сообщений
            if client_mode == LISTEN_MODE:
                LOG.info(f'Режим {LISTEN_MODE}')
                try:
                    listen_message_from_server(get_message(client_socket))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOG.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)
                except Exception as err:
                    LOG.error(f'Attention! {err}')
                    sys.exit(1)


if __name__ == '__main__':
    main()
