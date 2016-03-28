# -*- coding: utf8 -*-
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from message import Request, Response
from connection import Connection
from threading import Thread
from select import select
import logging


logger = logging.getLogger(__name__)


class ProxyHandler(Thread):
    def __init__(self, conn, addr):
        super(ProxyHandler, self).__init__()
        self.client_conn = conn
        self.client_addr = addr
        self.server_conn = None

    def run(self):
        try:
            self.loop()
        finally:
            # self.socket.close()
            self.client_conn.close()

    def _proceed_request(self, data):
        if self.server_conn:
            self.server_conn.write(data)
            return

        request = Request.parse(data)

        if request.method == 'CONNECT':
            server, port = request.uri.split(':')
        else:
            server, port = request.headers['Host'], 80

        conn = socket(AF_INET, SOCK_STREAM)
        conn.connect((server, port))
        self.server_conn = Connection(conn)

        self.client_conn.sendall('Hello')

        # TODO connect to server, transfer request, check cache headers

    def loop(self):
        while True:
            rlist, wlist, xlist = self._prepare_socket_lists()
            r, w, x = select(rlist, wlist, xlist, 1)

    def _prepare_socket_lists(self):
        rlist, wlist, xlist = [self.client_conn], [], []


class ProxyServer(object):
    socket = None

    def __init__(self, host, port, backlog=100):
        self.host = host
        self.port = port
        self.backlog = backlog

    def run(self):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.backlog)

            while True:
                conn, addr = self.socket.accept()
                connection = Connection(conn)
                handler = ProxyHandler(connection, addr)
                handler.daemon = True
                handler.start()
        finally:
            logger.info('Closing main socket')
            self.socket.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - pid:%(process)d - %(message)s'
    )
    proxy = ProxyServer('', 8000)
    proxy.run()
