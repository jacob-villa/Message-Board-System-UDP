import json
import random
import socket
import threading


# Initialize UDP client socket
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
buffer_size = 1024


# Server connection details
server_addr = None
server_port = None


# Main program logic
def send_to_server(cmd: str, handle: str = None, msg: str = None):
    # Build command object
    message = {
        "command": cmd
    }
    if handle is not None:
        message["handle"] = handle
    if msg is not None:
        message["message"] = msg
    
    # Encode command object as string
    message_json = json.dumps(message)

    # Send JSON-encoded command to server
    client_sock.sendto(message_json.encode(), (server_addr, server_port))


def recv_from_server():
    while True:
        try:
            # Wait for response
            response_packet, _ = client_sock.recvfrom(buffer_size)
            response_decoded = response_packet.decode()

            # Decode server response JSON
            response = json.loads(response_decoded)

            # Parse command
            cmd = response["command"]
            if cmd == "join":
                print("Connection to the Message Board Server is successful!")
            elif cmd == "leave":
                print("Connection closed. Thank you!")
            elif cmd == "register":
                print("Welcome {0}!".format(cmd["handle"]))
            elif cmd == "all":
                print("{0}: {1}".format(cmd["handle"], cmd["message"]))
            elif cmd == "msg":
                print("[from {0}] {1}".format(cmd["handle"], cmd["message"]))
            elif cmd == "error":
                print("Error: {0}".format(cmd["message"]))
        except:
            pass


def join_server():
    # Bind client socket to random port
    client_sock.bind(('localhost', random.randint(8000, 9000)))

    # Send join message to server
    send_to_server('join')


def error_check(cmd: str, args: list) -> bool:
    # Error checking for command syntax
    if cmd not in ["/join", "/leave", "/register", "/all", "/msg", "/?"]:
        print("Error: Command not found.")
        return False

    # Checking errors for /join
    if cmd == "/join":
        if not args[1].isDigit():
            print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
            return False

        if server_addr is not None and server_port is not None:
            print("Error: Already connected to a server.")
            return False

    # Checking errors for /leave
    if cmd == "/leave":
        if server_addr is None or server_port is None:
            print("Error: Disconnection failed. Please connect to the server first.")
            return False
        elif len(args) > 0:
            print("Error: Command parameters do not match or is not allowed.")
            return False

    # Checking errors for /register
    if cmd == "/register" and len(args) > 1:
        print("Error: Command parameters do not match or is not allowed.")
        return False

    # Checking errors for /?
    if cmd == "/?" and len(args) > 0:
        print("Error: Command parameters do not match or is not allowed.")
        return False

    return True

# Creating thread for receiving replies from server
recv_thread = threading.Thread(target = recv_from_server)
recv_thread.start()


# Main loop for receiving CLI input
while True:
    # Input from CLI
    client_message = input()
    client_cmdline = client_message.strip(' ').split(' ')

    # Split command line into command and arguments
    client_cmd = client_cmdline[0]
    client_args = client_cmdline[1:]

    # Check command line for errors
    if not error_check(client_cmd, client_args):
        continue

    # Parse commands
    if client_cmd == "/join":
        # Save server details
        server_addr = client_args[0]
        server_port = int(client_args[1])

        # Join server
        join_server()
    elif client_cmd == "/register":
        send_to_server("register", handle=client_args[0])
    elif client_cmd == "/all":
        send_to_server("all", msg=' '.join(client_args))
    elif client_cmd == "/msg":
        send_to_server("msg", handle=client_args[0], msg=' '.join(client_args[1:]))
    elif client_cmd == "/?":
        print("""
        COMMANDS:\n\n
        Connect to a server\t-\t/join <server_ip_add> <port>\n
        Disconnect from the server\t-\t/leave\n
        Register a unique handle or alias\t-\t/register <handle>\n
        Send a message to all users in server\t-\t/all <message>\n
        Send a direct message to a user\t-\t/msg <handle> <message>\n
        View commands\t-\t/?\n\n
        """)
    elif client_cmd == "/leave":
        # Delete connection details
        client_sock.close()
        server_addr = None
        server_port = None
