import sys
import time
from socket import *
import json

from common.variables import *
from common.utils import send_message, get_message

def get_answer(msg):
    '''get answer from server'''
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            return '200 : OK'
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
    # client.py 192.168.1.2 8079
    try:
        server_address = sys.argv[2]
        server_port = int(sys.argv[3])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)
    # create socket and make connection
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_address, server_port))
    # make and send presence-message (say hello to server)
    msg = make_presence()
    send_message(client_socket, msg)
    # get an answer from server
    try:
        answer = get_answer(get_message(client_socket))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
