# -*- coding: utf8 -*-
import logging
import socket


logger = logging.getLogger(__name__)


class Connection(object):
    """Connection abstraction"""
    def __init__(self, socket_conn):
        self.conn = socket_conn
        self.write_buffer = ''

        self.closed = False
        # TODO makeshift. Remake with select.select
        self.conn.setblocking(0)

    def write(self, data):
        sent = self.conn.send(self.write_buffer)
        self.write_buffer = self.write_buffer[sent:]

        self.write_buffer += data

    def flush(self):
        sent = self.conn.send(self.write_buffer)
        self.write_buffer = self.write_buffer[sent:]

    def close(self):
        if not self.closed:
            self.conn.close()
            self.closed = True

    def read(self, bufsize=8192):
        # TODO start only when socket is read-ready
        data = ''
        try:
            while True:
                data += self.conn.recv(bufsize)
                if len(data) == 0:
                    return None
        except socket.error:
            return data or None
