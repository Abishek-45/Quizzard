class HttpRequest:
    def __init__(self, method, url, version='HTTP/1.1'):
        self.method = method
        self.url = url
        self.version = version
        self.headers = {}
        self.body = None

    def add_headers(self, key, value):
        self.headers[key] = value
    
    def set_body(self, body):
        self.body = body
    
    def build_packet(self):
        packet = f'{self.method} {self.url} {self.version}\r\n'

        for key, value in self.headers.items():
            packet += f"{key} : {value}\r\n"
        packet += '\r\n'
        
        if self.body:
            packet += self.body

        return packet
    
class HttpResponse:
    def __init__(self, status_code, reason_phrase, version="HTTP/1.1"):
        self.version = version
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.body = None
        self.headers = {}
    
    def add_header(self, key, value):
        self.headers[key] = value
    
    def set_body(self, body):
        self.body = body

    def build_headers(self):
        packet = f'{self.version} {self.status_code} {self.reason_phrase}\r\n'

        for key, value in self.headers.items():
            packet += f'{key}: {value}\r\n'

        packet += '\r\n'
        return packet
    
    def build_packet(self):
        packet_headers = self.build_headers()
        return packet_headers.encode('utf-8'), self.body