import socket
from http_protocol import HttpResponse
import json
import http.server

host = '127.0.0.1'
port = 8888

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((host, port))
server_sock.listen(1)

try:
    print(f"Listening on {host}:{port}")
    client, addr = server_sock.accept()
    print(f"Connection from {addr}")

    client.settimeout(10)
    while True:
        try:
            request_message = client.recv(1024).decode('utf-8')
            parse = request_message.split()
            print(parse)
            message = "<html><body><h1>Hello World!</h1></body></html>"
            
            response_object = HttpResponse(200, 'OK')
            response_object.add_header('Content-Type', 'text/html')
            response_object.add_header('Content-Length', str(len(message)))
            response_object.set_body(message)

            response_packet = response_object.build_packet()
            client.send(response_packet.encode('utf-8'))

        except socket.timeout:
            response_object = HttpResponse(408, 'Request Timeout')
            response_object.add_header('Content-type','text/html')
            packet = response_object.build_packet()
            client.send(packet.encode('utf-8'))
            print("Closing connection")
            client.close()
        
except Exception as e:
    print(f"Something went wrong: {e}")

server_sock.close()
