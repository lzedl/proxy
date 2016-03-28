# -*- coding: utf8 -*-
"""Work only on complete message data"""
from collections import OrderedDict, Iterator
from abc import ABCMeta, abstractmethod


CRLF = '\r\n'


class HttpDataIterator(Iterator):
    def __init__(self, raw_data):
        self.data = raw_data
        self.prev_pos = 0
        self.pos = 0

    def next(self):
        self.pos = self.data.find(CRLF, self.prev_pos)
        if self.pos < 0:
            raise StopIteration
        chunk = self.data[self.prev_pos:self.pos]
        self.prev_pos = self.pos + len(CRLF)
        return chunk

    def rest(self):
        return self.data[self.prev_pos:]


class HttpMessage(object):
    __metaclass__ = ABCMeta
    version = None
    headers = None
    body = ''

    def __init__(self):
        self.headers = OrderedDict()

    @classmethod
    def parse(cls, data):
        """Return HttpMessage instance with data parsed from data

        :param str data:
        :rtype: HttpMessage
        """
        instance = cls()

        it = HttpDataIterator(data)
        instance._parse_start_line(it.next())

        for line in it:
            if not line:
                break
            instance._parse_header_line(line)

        instance.body = it.rest()

        return instance

    @abstractmethod
    def _parse_start_line(self, line):
        pass

    def _parse_header_line(self, line):
        k, v = line.split(':', 1)
        self.headers[k.strip()] = v.strip()


class Request(HttpMessage):
    method = None
    uri = None

    def _parse_start_line(self, line):
        values = line.split(' ', 2)

        self.method = values[0].upper()
        self.uri = values[1]
        self.version = values[2]


class Response(HttpMessage):
    code = None
    reason = ''

    def _parse_start_line(self, line):
        values = line.split(' ', 2)

        self.version = values[0]
        self.code = int(values[1])
        self.reason = values[2]
