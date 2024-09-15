import socket
import threading

port = 8888
host = '127.0.0.1'

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((host, port))

'''
Before everything there should be a HTTP server listening to a port for a HOST_CLIENT to initiate a process.
This particular port creates a thread running the function "host_function" to handle the HOST_CLIENT
'''

def host_function(host_client, host_addr):
    # This function handles the host client initiating the quiz app
    ''' 
        Step 1: The host_client creates a quiz and makes it active in the internet for the clients to get connected
    After making it active the client_connection thread can be started for the server to listen to the clients
    Once the quiz gets started the clients "client_connections" thread will be severed and the clients can take the 
    test.

        Step2: 
    '''
    pass

def handle_client(sock, addr):
    # This handles all the clients that are taking the quiz
    pass

# Before the client's are connected, there should be a host to initiate the process(Quiz)
def client_connections():
    while True:
        # Server should listen for client's connection
        client_sock, client_addr = server_sock.accept()
        client_thread = threading.Thread(handle_client, args=[client_sock, client_addr], daemon=True)
        client_thread.start()

        # When the connnections are made, their respective username and their address will be stored by the host_function 
        # Thread
        print(f'Connection from {client_addr}')

# Waiting for host_client to initiate a process
while True:
    host_client_sock, host_addr = server_sock.accept()
    host_thread = threading.Thread(host_function, args=[host_client_sock, host_addr], daemon=True)
    host_thread.start()