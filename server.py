import json
import sys
from socket import socket, AF_INET, SOCK_STREAM

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS,PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message


def check_message(msg):
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {RESPONSE: 400, ERROR: 'Bad request'}


def main():
    # server.py -p 8888 -a 192.168.1.33
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print(
            'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        print(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)
    # create servers socket
    print(listen_address, listen_port)
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((listen_address, listen_port, ))

    server_socket.listen(MAX_CONNECTIONS)
    # endless cycle to waiting clients
    while True:
        client_socket, client_addr = server_socket.accept()
        try:
            clients_message = get_message(client_socket)
            print(clients_message)
            response = check_message(clients_message)
            send_message(client_socket, response)
            client_socket.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')
            client_socket.close()



if __name__ == '__main__':
    main()

