import socket
import threading
import signal
import sys
from http_protocol import HttpResponse
import os
import json
import random
import sqlite3


host = '127.0.0.1'
port = 8888
server_sock = None  # Declare this globally so it can be accessed in the signal handler

create_quest_lock = threading.Lock()
condition = threading.Condition()

shared_data = {
            "questions": [
            {
            "id": 1,
            "question": "What is the capital of France?",
            "options": ["Paris", "London", "Berlin", "Rome"],
            "answer": "Paris"
            },
            {
              "id": 2,
              "question": "Who wrote 'Hamlet'?",
              "options": ["William Shakespeare", "Charles Dickens", "J.K. Rowling", "Leo Tolstoy"],
              "answer": "William Shakespeare"
            }
            ]
        }
code_map = {1234 : ["Host", []]}
code_question = {}
code_map_count = {}

resources = {
             '/' : r'E:\Quizzard\Quizzard\Socket\http_webserver\frontend\main.html',
             '/join.html' : r'E:\Quizzard\Quizzard\Socket\http_webserver\frontend\join.html',
             '/leader.html' : r'E:\Quizzard\Quizzard\Socket\http_webserver\frontend\leader.html',
             '/style.css' : r'E:\Quizzard\Quizzard\Socket\http_webserver\frontend\style.css',
             '/create.html' : r'E:\Quizzard\Quizzard\Socket\http_webserver\frontend\create.html',
             '/lobby.html' : r'E:\Quizzard\Quizzard\Socket\http_webserver\lobby.html',
             '/index.html' : r'E:\Quizzard\Quizzard\Socket\http_webserver\frontend\index.html',
            }

resources_type = {
    'document' : 'text/',
    'style' : 'text/',
    'image' : 'image/',
}

# Synchronize this function to avoid assigning the same code for two hosting clients
def join_code(client):
    code = random.randrange(100000, 999999)
    while code in code_map:
        code = random.randrange(100000, 999999)
    code_map[code] = [[client], []]         #[[Host], [Client1, Client2, Client3]]
    # response_object = HttpResponse(200, 'OK')
    # response_object.add_header('Content-Type', 'application/json')
    # json_body = json.dumps({"data": code})
    # response_object.set_body(json_body)
    # response_object.add_header('Content-Length', len(json_body))
    # response_packet, body = response_object.build_packet()
    return code

# To get questions from the host and preprocess it.

def create_quest(client, *args, **kwargs):
    with create_quest_lock:
        body = json.loads(args[0])
        code = join_code(client)
        code_question[code] = body
        global shared_data
        shared_data = body
        print("Shared Data : ",shared_data)
    response_object = HttpResponse(302, "Found")
    response_object.add_header('Content-Type', 'application/json')
    jsonCode = json.dumps({'code' : code}).encode('utf')
    response_object.set_body({'code' : code})
    response_object.add_header('Content-Length', len(jsonCode))
    response_packet, body = response_object.build_packet()
    client.send(response_packet)
    client.sendall(jsonCode)

def join_quiz(client, *args, **kwargs):
    body = json.loads(args[0])
    code = body['client_code']
    if code in code_map:
        code_map[code][1].append(client)
        print("Code Map : ",code_question[code])
        response_object = HttpResponse(302, "Found")
        response_object.add_header('Content-Type', 'application/json')
        response_object.add_header('Content-Length', 0)
        response_packet, _ = response_object.build_packet()
        client.send(response_packet)
    else:
        response_object = HttpResponse(404, "Not Found")
        response_packet, body = response_object.build_packet()
        client.send(response_packet)

'''

def start_quiz(client, *args, **kwargs):
    
    Once the count of the responses equals
    the total number of clients, the user will 
    be redirected to the leaderboard page along
    with the score and name information.

    Before the quiz starts the code will be
    deleted from the map so the user cannot join
'''

def start_quiz(client, *args, **kwargs):
    global shared_resource
    body = json.loads(args[0])


def get_quiz_data(client, *args, **kwargs):
    global shared_data
    if shared_data:
        response_object = HttpResponse(200, 'OK')
        response_object.add_header('Content-Type','application/json')
        dataObject = {"data" : shared_data}
        jsonData = json.dumps(dataObject).encode('utf-8')
        response_object.add_header('Content-Length', len(jsonData))
        response_object.set_body(dataObject)
        response_packet, body = response_object.build_packet()
        client.send(response_packet)
        client.sendall(jsonData)
    else:
        response_object = HttpResponse(404, "Not Found")
        response_packet, body = response_object.build_packet()
        client.send(response_packet)

class HandleError(Exception):
    status_map = {
            404 : 'Not Found', 
            200 : 'OK', 
            400 : 'Bad Request', 
            401 : 'Unauthorized', 
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

def refresh(client, *args, **kwargs):
    refresh_code = kwargs['params']
    if refresh_code:
        if code_map[refresh_code['code']]:
            response_object = HttpResponse(200, 'OK')
            response_object.add_header('Content-Type','application/json')
            count = len(code_map[refresh_code['code']][1])
            jsonCount = json.dumps({"people" : count}).encode('utf')
            response_object.add_header('Content-Length', len(jsonCount))
            response_object.set_body({"people" : count})
            response_packet, body = response_object.build_packet()
            print("Inside Refresh : ",count)
            client.send(response_packet)
            client.sendall(jsonCount)
        else:
            response_object = HttpResponse(404, 'Not Found')
            response_packet, _ = response_object.build_packet()
            client.send(response_packet)
            print("Code Not Found")
    else:
        print("No Parameters passed")

def handle_get(client, req_path):
    if '?' in req_path:
        path, params = req_path.split('?')
    else:
        path = req_path
        params = None
    handle = url_patterns.get(path)
    response_packet, body = handle(client)
    return response_packet, body

def handle_post(client, req_path, body):
    handle = url_patterns.get(req_path)
    handle(client, body)

def redirect_teach(client, *args, **kwargs):
    print(kwargs['params'])

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
            try:
                if parse[0] == 'GET':
                    file_object, file_extension = fetch_file(parse[1])
                    if file_object:
                        dest_type = headers.get('Sec-Fetch-Dest', 'document')
                        content_type = fileType(dest_type, file_extension)
                        response_object = HttpResponse(200, 'OK')
                        response_object.add_header('Content-Type', content_type)
                        response_object.add_header('Content-Length', str(len(file_object)))
                        packet_headers, body = response_object.build_packet()
                        client.send(packet_headers)
                        if isinstance(file_object, str):
                            client.sendall(file_object.encode('utf-8'))
                        else:
                            client.sendall(file_object)
                    else:
                        response_header, body = handle_get(client, parse[1])
                        client.sendall(response_header)
                        client.sendall(body.encode('utf-8'))
                elif parse[0] == 'POST':
                    handle_post(client, parse[1], headers['body'])
                    # response_object = HttpResponse(200, 'OK')
                    # response_object.add_header('Content-type', 'application/json')
                    # response_object.set_body({"answer" : 2})
                    # response_packet, body = response_object.build_packet()
                    # client.send(response_packet)
                    # if body:
                    #     client.send(json.dumps(body).encode('utf-8'))
                else:
                    raise HandleError('Bad Request', 400)
            except HandleError as e:
                error_packet = e.handle_error()
                print(error_packet)
                client.sendall(error_packet.encode('utf-8'))
                print(f"Error : {e}")
            except Exception as e:
                print("Server Error : ", e)
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

# Server Object
url_patterns = {}
url_patterns['/api/join-code/'] = join_code
url_patterns['/api/create/'] = create_quest
url_patterns['/api/join-quiz/'] = join_quiz
url_patterns['/api/data/'] = get_quiz_data
url_patterns['/teach_wait.html'] = redirect_teach
url_patterns['/api/start-quiz/'] = start_quiz
url_patterns['/api/refresh/'] = refresh

try:
    server_sock.listen(10)
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