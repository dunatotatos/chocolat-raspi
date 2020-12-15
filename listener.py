import socket
import logging

import constant

LOG = logging.getLogger(__name__)


def server_program():
    host = constant.IP_SRV  # socket.gethostname()
    port = constant.PORT_SRV  # initiate port no above 1024
    server_socket = socket.socket()  # get instance
    server_socket.bind((host, port))  # bind host address and port together

    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection
    a = str()
    data = conn.recv(1024).decode()
    for i, k in enumerate(data[5:]):
        if i is 0: a = k
        elif k is " ":
            LOG.debug("-{}-".format(a))
            break
        else:
            a += k
    conn.send(data.encode())  # send data to the client
    conn.close()  # close the connection
    return a
