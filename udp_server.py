import json
import socket
import threading
import queue

# Client class
class client:
    def __init__(self, addr: tuple, handle: str = None):
        self.addr = addr


# Messages and list of clients
msg_queue = queue.Queue()
client_list = []


# Initialize server socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bufferSize = 1024


# Server details and socket binding
server_addr = socket.gethostname()
server_port = 20001
server_sock.bind((server_addr, server_port))


def recv_from_clients():
    while True:
        try:
            client_msg, client_addr = server_sock.recvfrom(bufferSize)
            msg_queue.put((client_msg.decode(), client_addr))
        except:
            pass


def create_reply(msg: str, addr: tuple) -> dict:
    global client_list
    
    reply = {}
    
    # Get message in dict format
    msg_json = json.loads(msg)

    # Get command from message
    cmd = msg_json["command"]

    # Receive /join from client
    if cmd == "join":
        if any(client for client in client_list if client.addr == addr):
            reply["command"] = "error"
            reply["message"] = "Current client has already joined the server."
        else:
            reply["command"] = "join"
    elif cmd == "leave":
        if any(client for client in client_list if client.addr == addr):
            # NOTE: Replaces the existing client_list with a new object 
            client_list = [client for client in client_list if client.addr != addr]
            reply["command"] = "leave"

        #TODO: Make replies for all other commands, figure out how to send to recipient

    return reply


def send_to_clients():
    while True:
        while not msg_queue.empty():
            current_msg, current_addr = msg_queue.get()

            if not any(client for client in client_list if client.addr == current_addr):
                client_list.append(client(current_addr))

            """ for client in client_list:
                try:
                    if current_msg.decode("utf-8").startswith("SIGNUP_TAG:"):
                        clientName = current_msg.decode()[current_msg.decode().index(":") + 1 : ]
                        server_sock.sendto(f"Welcome {clientName}!".encode(), client)
                    else:
                        server_sock.sendto(current_msg, client)
                except:
                    client_list.remove(client) """

            # Call create_reply(), turn return val into JSON with json.dumps, sendto client


recv_thread = threading.Thread(target = recv_from_clients)
send_thread = threading.Thread(target = send_to_clients)

recv_thread.start()
send_thread.start()
