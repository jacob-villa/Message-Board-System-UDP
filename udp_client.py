import socket
import threading
from typing import List

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# server_IP = socket.gethostbyname(socket.gethostname())
# server_port = 20001
server_IP = None
server_port = None

bufferSize = 1024

# clientSocket.bind((server_IP, random.randint(8000, 9000)))

# clientName = input("Name: ")

def receive():
    while True:
        try:
            msg, addr = clientSocket.recvfrom(bufferSize)
            print(msg.decode())
        except:
            pass

def concatMessage(clientCommand: List[str]) -> List[str]:
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

def errorCheck(clientCommand: list):
    # Error checking for command syntax
    if clientCommand[0] not in ["/join", "/leave", "/register", "/all", "/msg", "/?"]:
        print("Error: Command not found.")
        return False

    # Checking errors for /join
    if clientCommand[0] == "/join":
        if not clientCommand[2].isDigit():
            print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
            return False

    # Checking errors for /leave
    if clientCommand[0] == "/leave":
        if server_IP is None or server_port is None:
            print("Error: Disconnection failed. Please connect to the server first.")
            return False
        elif len(clientCommand) > 1:
            print("Error: Command parameters do not match or is not allowed.")
            return False

    # Checking errors for /register
    if clientCommand[0] == "/register" and len(clientCommand) > 2:
        print("Error: Command parameters do not match or is not allowed.")
        return False

    # Checking errors for /?
    if clientCommand[0] == "/?" and len(clientCommand) > 1:
        print("Error: Command parameters do not match or is not allowed.")
        return False

    return True
    

thread = threading.Thread(target = receive)
thread.start()

# clientSocket.sendto(f"SIGNUP_TAG:{clientName}".encode(), (server_IP, server_port))

# print("UDP target IP: ", server_IP)
# print("UDP target Port: ", server_port)

while True:
    # input from cli
    clientMsg = input("")
    clientCommand = clientMsg.strip(' ').split(' ')

    # input:  clientMsg = "/all hello world"
    # output: clientCommand = ["/all", "hello world"]
    # input:  clientMsg = "/msg Deckard hello world again"
    # output: clientCommand = ["/msg", "Deckard", "hello world again"]
    if clientCommand[0] == "/all" or clientCommand[0] == "/msg":
        clientCommand = concatMessage(clientCommand)

    #if errorCheck(clientCommand):


    if clientCommand[0] == "/join":
        server_IP = clientCommand[1]
        server_port = clientCommand[2]


    if clientCommand[0] == "/leave":
        print("Connection closed. Thank you!")
        exit()
    # else:
        # clientSocket.sendto(f"{clientName}: {clientMsg}".encode(), (server_IP, server_port))