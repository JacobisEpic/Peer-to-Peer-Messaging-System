import socket
import threading
import json

host = '127.0.0.1'
port = 55550

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

print(f"Server started on {host}:{port}")

clients = []
nicknames = []
chatrooms = []

def broadcast(message, chatroom):
    for i, client in enumerate(clients):
        if chatrooms[i] == chatroom:
            client.send(message)

def sanitize(data):
    """Simple sanitizer to remove any non-alphanumeric characters except space, hyphen, underscore."""
    import re
    return re.sub(r'[^a-zA-Z0-9 _-]', '', data)

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            message_data = message.split('|')
            if len(message_data) >= 3:
                # Sanitize chatroom ID, nickname, and message
                chatroom = sanitize(message_data[0])
                nickname = sanitize(message_data[1])
                user_message = sanitize('|'.join(message_data[2:]))  # Join back in case the message includes '|'
                
                broadcast_message = f"{chatroom}|{nickname}|{user_message}".encode('ascii')
                broadcast(broadcast_message, chatroom)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            chatroom = chatrooms[index]
            left_message = f"{chatroom}|{nickname}|left!".encode('ascii')
            broadcast(left_message, chatroom)
            nicknames.remove(nickname)
            chatrooms.remove(chatroom)
            break


# def handle(client):
#     while True:
#         try:
#             message = client.recv(1024).decode('ascii')
#             message_data = message.split('|')
#             chatroom = message_data[0]
#             broadcast_message = '|'.join(message_data).encode('ascii')
#             broadcast(broadcast_message, chatroom)
#         except:
#             index = clients.index(client)
#             clients.remove(client)
#             client.close()
#             nickname = nicknames[index]
#             chatroom = chatrooms[index]
#             left_message = f"{chatroom}|{nickname}|left!".encode('ascii')
#             broadcast(left_message, chatroom)
#             nicknames.remove(nickname)
#             chatrooms.remove(chatroom)
#             break

def receive():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        client.send('CHATROOM'.encode('ascii'))
        chatroom = client.recv(1024).decode('ascii')
        
        nicknames.append(nickname)
        clients.append(client)
        chatrooms.append(chatroom)

        print(f"Nickname: {nickname}, Chatroom: {chatroom}")
        broadcast(json.dumps({"nickname": nickname, "chatroom": chatroom, "message": "joined!"}).encode('ascii'), chatroom)
        client.send('Connected to server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()
