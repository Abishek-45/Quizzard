import socket
import threading
import signal
import sys
from http_protocol import HttpResponse
import os
import json

host = '127.0.0.1'
port = 8888

server_sock = None  # Declare this globally so it can be accessed in the signal handler

resources = {
             '/' : r'E:\Quizzard\Quizzard\Socket\http_webserver\quiz.html', 
             '/lets_play.html' : r'E:\Quizzard\Quizzard\Socket\http_webserver\lets_play.html',
             '/style.css' : r'E:\Quizzard\Quizzard\Socket\http_webserver\style.css',
             '/assests/chest.png' : r'E:\Quizzard\Quizzard\Socket\http_webserver\assests\chest.png',
             '/api/' : r'E:\Quizzard\Quizzard\Socket\http_webserver\forms.html',
             '/api/style.css' : r'E:\Quizzard\Quizzard\Socket\http_webserver\style.css',
            }

resources_type = {
    'document' : 'text/',
    'style' : 'text/',
    'image' : 'image/',
}

class HandleError(Exception):
    status_map = {
            404: 'Not Found', 
            200 : 'OK', 
            400 : 'Bad Request', 
            401: 'Unauthorized', 
            403 : 'Forbidden', 
            405 : 'Method Not Allowed', 
            408 : 'Request Timeout'
        }
    
    def __init__(self, message, value):
        self.message = message
        self.value = value
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.message} {self.value}'
    
    def handle_error(self):
        response_object = HttpResponse(
            status_code = self.value, 
            reason_phrase = self.__class__.status_map.get(self.value, 'Unknown Status')
        )
        response_packet = response_object.build_packet()
        return response_packet

def httpParser(request):
    request_line = request.split('\r\n')
    body = request_line.pop()
    first = request_line[0].split()
    headers = {}
    for header in request_line[1:]:
        element = header.split(': ', 1)
        if element[0]:
            key, value = element[0], element[1]
            headers[key] = value
    headers['body'] = body
    return first, headers

def fileType(dest_type, file_extension):
    content_type = ''
    if dest_type in resources_type:
        content_type = content_type + resources_type[dest_type] + file_extension[1:]
    else:
        content_type = 'application/octet-stream'
    return content_type

def fetch_file(url_path):
    try:
        if url_path in resources:
            _, file_extension = os.path.splitext(resources[url_path])
            read_mode = 'r' if file_extension in ['.html', '.css', '.js'] else 'rb'

            with open(resources[url_path], read_mode) as file:
                file_object = file.read()
            
            return file_object, file_extension
        else:
            raise HandleError('File Not Found', 404)
    except HandleError as e:
        error_packet = e.handle_error()
        return None, None
    except Exception as e:
        raise HandleError("Internal Server Error", 500)
    
def handle_client(client, addr):
    try:
        while True:
            request_obj = client.recv(1024).decode('utf-8')

            if not request_obj.split('\r\n'):  # Handle malformed requests
                response_packet = "HTTP/1.1 400 Bad Request\r\n\r\n"
                client.sendall(response_packet.encode('utf-8'))
                return
            
            parse, headers = httpParser(request_obj)
            print(parse)

            if 'Connection' in headers and headers['Connection'] == 'Close':
                client.close()
                return
            # parse = request_obj.split()
            try:
                if parse[0] == 'GET':
                    file_object, file_extension = fetch_file(parse[1])
                    if file_object:
                        dest_type = headers.get('Sec-Fetch-Dest', 'document')
                        content_type = fileType(dest_type, file_extension)
                        response_object = HttpResponse(200, 'OK')
                        response_object.add_header('Content-Type', content_type)
                        response_object.add_header('Content-Length', str(len(file_object)))
                        response_object.set_body(file_object)
                        packet_headers, body = response_object.build_packet()
                        client.send(packet_headers)
                        if isinstance(file_object, str):
                            client.sendall(file_object.encode('utf-8'))
                        else:
                            client.sendall(file_object)
                elif parse[0] == 'POST':
                    response_object = HttpResponse(200, 'OK')
                    response_object.add_header('Content-type', 'application/json')
                    # Request responded with the answer
                    response_object.set_body({"answer" : 2})
                    response_packet, body = response_object.build_packet()
                    client.send(response_packet)
                    if body:
                        client.send(json.dumps(body).encode('utf-8'))
                else:
                    raise HandleError('Bad Request', 400)
            except HandleError as e:
                error_packet = e.handle_error()
                print(error_packet)
                client.sendall(error_packet.encode('utf-8'))
                print(f"Error : {e}")
            except Exception as e:
                raise HandleError('File Not Found', 404)
    finally:
        print("Closing client...",addr)
        client.close() # Close connection after handling the request
        return

# Signal handler for Ctrl + C (SIGINT)
def signal_handler(sig, frame):
    print("Ctrl + C detected, shutting down the server...")
    if server_sock:
        server_sock.close()  # Close the server socket
    sys.exit(0)  # Exit the program

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Server code
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((host, port))

try:
    server_sock.listen(7)
    print(f"Server Listening on port {port}")
    while True:
        try:
            client, addr = server_sock.accept()
            print(f"Server connected to client {addr}")
            client_thread = threading.Thread(target=handle_client, args=[client, addr], daemon=True)
            client_thread.start()
        except KeyboardInterrupt:
            print("Server Shutting Down...")
            break
except Exception as e:
    print(f"Error {e}")
finally:
    if server_sock:
        server_sock.close()