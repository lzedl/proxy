# -*- coding: utf8 -*-
from collections import OrderedDict

CRLF = '\r\n'
PARSE_START_LINE = 1
PARSE_HEADERS = 2
PARSE_BODY = 3
PARSE_COMPLETE = 4


class HttpParser(object):
    request = None

    def __init__(self):
        self.stage = PARSE_START_LINE
        self.stage_func = self.parse_start_line
        self.buffer = ''
        self.pos = 0
        self.content_length = 0
        self.method = None
        self.uri = None
        self.version = None
        self.headers = OrderedDict()
        self.body = ''

    def feed(self, data):
        self.buffer += data
        self.parse()

    def parse(self):
        # TODO check stream and run stage func
        pass

    def parse_start_line(self):
        pos = self.buffer.find(CRLF, self.pos)
        if pos == -1:
            return

        start_line = self.buffer[self.pos:pos]

        if not start_line:
            self.pos = pos + len(CRLF)
            return

        method, uri, version = start_line.split()

        self.request.method = method.upper()
        self.request.uri = uri
        self.request.version = version

        self.stage = PARSE_HEADERS
        self.stage_func = self.parse_header
        self.pos = pos + len(CRLF)

    def parse_header(self):
        while True:
            pos = self.buffer.find(CRLF, self.pos)
            if pos == -1:
                return

            header_line = self.buffer[self.pos:pos]

            if not header_line:
                # TODO also check Transfer-Encoding: chunked
                if 'Content-Length' in self.headers:
                    self.content_length = int(self.headers['Content-Length'])
                    self.stage_func = self.parse_body
                    self.stage = PARSE_BODY
                else:
                    self.stage_func = self.parse_start_line
                    self.stage = PARSE_COMPLETE
            else:
                k, v = header_line.split(':', 1)
                self.request.headers[k.strip()] = v.strip()

    def parse_body(self):
        if self.unparsed_buffer_size() <= self.content_length:
            self.body += self.buffer[self.pos:self.pos + self.content_length]
            self.buffer = self.buffer[self.pos + self.content_length:]
            self.pos = 0

    def clear(self):
        self.method = None
        self.uri = None
        self.version = None
        self.headers = OrderedDict()
        self.body = ''

    def unparsed_buffer_size(self):
        return len(self.buffer) - self.pos
