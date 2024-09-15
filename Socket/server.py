import socket
import json

def score(client_answer):
    count = 0
    for i in range(len(client_answer)):
        if client_answer[i] is not None and int(client_answer[i]) == answers[i]:
            count += 1
    return count

host = '127.0.0.1'
port = 8000
BUF_SIZE = 256
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)

questions = ['1 + 1 = ?', '3 * 4 = ?']
answers = [2, 12]
client_answer = []
while True:
    client, addr = server.accept()
    
    # Receive data and decode as JSON
    response = client.recv(1024).decode('utf-8')
    try:
        response = json.loads(response)  # Convert string to dictionary
    except json.JSONDecodeError:
        response = {'connection': 'close', 'content': 'Invalid message'}
    
    if 'connection' in response and response['connection'] == 'close':
        break

    if response['content'].lower() == 'start':
        response['content'] = "Your test starts now"
        client.send(json.dumps(response).encode('utf-8'))  # Send as JSON

        for question in questions:
            response['content'] = question
            client.send(json.dumps(response).encode('utf-8'))  # Send as JSON

            response = client.recv(1024).decode('utf-8')

            # Receive answer from client and parse it
            response = json.loads(response)
            if 'connection' in response and response['connection'] == 'close':
                print("Exiting!!!")
                break
            
            answer = response['content']
            if answer:
                client_answer.append(answer)
            else:
                client_answer.append(None)

        # Send the final score
        response['content'] = f"Your test score: {score(client_answer)}"
        response['connection'] = 'close'
        client.send(json.dumps(response).encode('utf-8'))  # Send as JSON
    else:
        response = {'connection': 'close', 'content': 'Please try again'}
        client.send(json.dumps(response).encode('utf-8'))  # Send as JSON
    
    client.close()
server.close()