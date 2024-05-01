import socket
import threading
import json

nickname = input("Choose your nickname: ")
chatroom = input("Choose your chatroom (1, 2, or 3): ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(('127.0.0.1', 55550))
    print("Connected to the chat server successfully.")
except:
    print("Failed to connect to the chat server.")
    exit()

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            message_data=message.split('|')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif message == 'CHATROOM':
                client.send(chatroom.encode('ascii'))
            else:
                if len(message_data) == 3:
                    userName = message_data[1]
                    userMessage= message_data[2]
                    total = userName + ': ' + userMessage
                    print(total)
        except:
            print("An error occurred!")
            client.close()
            break

def sanitize(data):
    """Simple sanitizer to remove any non-alphanumeric characters except space, hyphen, underscore."""
    import re
    return re.sub(r'[^a-zA-Z0-9 _-]', '', data)

def write():
    while True:
        message = input('')
        sanitized_message = sanitize(message)
        message_data = f"{chatroom}|{nickname}|{sanitized_message}"
        client.send(message_data.encode('ascii'))


# def write():
#     while True:
#         message = input('')
#         message_data = f"{chatroom}|{nickname}|{message}"
#         client.send(message_data.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
