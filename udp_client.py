import socket
import threading
import random

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# server_IP = socket.gethostbyname(socket.gethostname())
# server_port = 20001
server_IP = None
server_port = None

bufferSize = 1024

clientSocket.bind((server_IP, random.randint(8000, 9000)))

clientName = input("Name: ")

def receive():
    while True:
        try:
            msg, addr = clientSocket.recvfrom(bufferSize)
            print(msg.decode())
        except:
            pass

def concatMessage(clientCommand: list):
    command = list(clientCommand[0])

    if clientCommand[0] == "/all":
        message = ' '.join(clientCommand[1 : ])
        command.append(message)

    elif clientCommand[0] == "/msg":
        handle = clientCommand[1]
        message = ' '.join(clientCommand[2 : ])
        command.append(handle)
        command.append(message)

    return command


thread = threading.Thread(target = receive)
thread.start()

clientSocket.sendto(f"SIGNUP_TAG:{clientName}".encode(), (server_IP, server_port))

print("UDP target IP: ", server_IP)
print("UDP target Port: ", server_port)

while True:
    clientMsg = input("")
    clientCommand = clientMsg.strip(' ').split(' ')

    if clientCommand[0] == "/all" or clientCommand[0] == "/msg":
        clientCommand = concatMessage(clientCommand)

    if clientCommand[0] == "/join":
        server_IP = clientCommand[1]
        server_port = clientCommand[2]

    if clientCommand[0] == "/leave":
        print("Connection closed. Thank you!")
        exit()
    else:
        clientSocket.sendto(f"{clientName}: {clientMsg}".encode(), (server_IP, server_port))