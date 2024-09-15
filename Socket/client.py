import socket
import json

host = '127.0.0.1'
port = 8000
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((host, port))
request = {}

try:
    clientMsg = input("Type 'Start' to start \n")
    request['content'] = clientMsg
    client_sock.send(json.dumps(request).encode('utf-8'))  

    response = client_sock.recv(1024).decode('utf-8')
 
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        print("Failed to decode the server's response")
        client_sock.close()
        exit(1)
    
    if 'connection' in response and response['connection'] == 'close':
        print("Server has closed the connection")
    else:
        print(response['content'])

        while True:
            response = client_sock.recv(1024).decode('utf-8')
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                print("Failed to decode the server's response")
                break
            
            if 'connection' in response:
                print(response['content'])
                break

            print(response['content'])
            answer = int(input("Answer: "))
            
            # Prepare the request with the user's answer
            request = {'content': answer}
            client_sock.send(json.dumps(request).encode('utf-8'))  # Send the answer to the server


except KeyboardInterrupt:
    request['connection'] = 'close'
    client_sock.send(json.dumps(request).encode('utf-8'))
    print("Exited by User")
except socket.error as e:
    print(f"Socket error: {e}")
finally:
    client_sock.close()
