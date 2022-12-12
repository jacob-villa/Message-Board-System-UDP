import json
import socket
import threading
import queue

# Client class
class client:
    def __init__(self, addr: tuple, handle: str = None):
        self.addr = addr
        self.handle = handle


# Messages and list of clients
msg_queue = queue.Queue()
client_list = []


# Initialize server socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bufferSize = 1024


# Server details and socket binding
# server_addr = socket.gethostname()
server_addr = '127.0.0.1'
server_port = 12345
server_sock.bind((server_addr, server_port))
print("Server is running")


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

    current_client = next((client for client in client_list if client.addr == addr), None)
    
    # Get message in dict format
    msg_json = json.loads(msg)

    # Get command from message
    cmd = msg_json["command"]

    if cmd == "join":
        if current_client is not None:
            reply["command"] = "error"
            reply["message"] = "Current client has already joined the server."
        else:
            client_list.append(client(addr))
            print("Client with address {0} has been added to the client list.".format(addr))
            reply["command"] = "join"
    elif cmd == "leave":
        # NOTE: Replaces the existing client_list with a new object 
        client_list = [client for client in client_list if client.addr != addr]
        print("Client with address {0} has disconnected, removing from client list.".format(addr))
        reply["command"] = "leave"
    elif cmd == "register":
        try:
            if any(client for client in client_list if client.handle == msg_json["handle"]):
                reply["command"] = "error"
                reply["message"] = "Registration failed. Handle or alias already exists."
            elif current_client.handle is None:
                current_client.handle = msg_json["handle"]
                print("Client with address {0} has registered the handle {1}.".format(addr, current_client.handle))
                reply["command"] = "register"
                reply["handle"] = msg_json["handle"]
            else:
                reply["command"] = "error"
                reply["message"] = "A handle has already been registered."
            
            
        except:
            pass
    elif cmd == "all":
        if current_client.handle is not None:
            reply["command"] = "all"
            reply["message"] = msg_json["message"]
            reply["handle"] = current_client.handle
        else:
            reply["command"] = "error"
            reply["message"] = "Cannot send messages without registering a handle."
    elif cmd == "msg":
        if current_client.handle is not None:
            if not any(client for client in client_list if client.handle == msg_json["handle"]):
                reply["command"] = "error"
                reply["message"] = "Handle or alias not found."
            else:
                # Reply is for the message recipient, not the sender 
                reply["command"] = "msg"
                reply["handle"] = current_client.handle
                reply["message"] = msg_json["message"]
        else:
            reply["command"] = "error"
            reply["message"] = "Cannot send messages without registering a handle."

    return reply


def send_to_clients():
    while True:
        while not msg_queue.empty():
            current_msg, current_addr = msg_queue.get()

            reply = create_reply(current_msg, current_addr)

            reply_json = json.dumps(reply)

            # Sending replies to respective recipients
            if reply["command"] in ["error", "join", "leave", "register"]:
                server_sock.sendto(reply_json.encode(), current_addr)
            elif reply["command"] == "all":
                for client in client_list:
                    if client.handle is not None:
                        server_sock.sendto(reply_json.encode(), client.addr)
            elif reply["command"] == "msg":
                # Echo the original message back to the sender client
                server_sock.sendto(current_msg.encode(), current_addr)
                
                # Since handle of the reply is the sender instead of the recipient,
                # need to get the recipient handle from the message
                msg_json = json.loads(current_msg)
                recipient_handle = msg_json["handle"]
                recipient_addr = next(client for client in client_list if client.handle == recipient_handle).addr
                server_sock.sendto(reply_json.encode(), recipient_addr)
                


recv_thread = threading.Thread(target = recv_from_clients)
send_thread = threading.Thread(target = send_to_clients)

recv_thread.start()
send_thread.start()
