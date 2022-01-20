import json

from .variables import MAX_PACKAGE_LENGTH, ENCODING


def get_message(client):
    '''
    Get bytes, decode to json, from json loads to dictionary
    and return object dict or raise error
    client.py 192.168.1.33 8888
    '''
    byte_client_data = client.recv(MAX_PACKAGE_LENGTH)
    if type(byte_client_data) is bytes:
        json_client_data = byte_client_data.decode(ENCODING)
        client_data = json.loads(json_client_data)
        if type(client_data) is dict:
            return client_data
        else:
            raise ValueError
    else:
        raise ValueError

def send_message(socket, msg):
    '''
    from str to bytes and sending message in byte-format
    '''
    json_msg = json.dumps(msg)
    byte_msg = json_msg.encode(ENCODING)
    socket.send(byte_msg)