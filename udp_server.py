import socket
import threading
import queue


messagesQueue = queue.Queue()
clientsList = []

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_IP = socket.gethostname()
server_port = 20001

bufferSize = 1024

serverSocket.bind((server_IP, server_port))


def receive():
    while True:
        try:
            print("Waiting for client...")
            
            msg, addr = serverSocket.recvfrom(bufferSize)
            messagesQueue.put((msg, addr))

        except:
            pass

def broadcast():
    while True:
        while not messagesQueue.empty():
            currentMessage, currentAddr = messagesQueue.get()

            print(currentMessage.decode())
            print("Client IP Address: {}".format(currentAddr))

            if currentAddr not in clientsList:
                clientsList.append(currentAddr)

            for client in clientsList:
                try:
                    if currentMessage.decode("utf-8").startswith("SIGNUP_TAG:"):
                        clientName = currentMessage.decode()[currentMessage.decode().index(":") + 1 : ]
                        serverSocket.sendto(f"Welcome {clientName}!".encode(), client)
                    else:
                        serverSocket.sendto(currentMessage, client)
                except:
                    clientsList.remove(client)


receiveThread = threading.Thread(target = receive)
broadcastThread = threading.Thread(target = broadcast)

receiveThread.start()
broadcastThread.start()
