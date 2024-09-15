import socket
import threading

host = '127.0.0.1'
port = 8888

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)