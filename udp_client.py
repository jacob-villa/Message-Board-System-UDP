import json
import random
import socket
import threading
import time


# Initialize UDP client socket
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_sock.settimeout(5)
buffer_size = 1024


# Server connection details
server_addr = None
server_port = None

client_sock.bind(('localhost', random.randint(8000, 9000)))

# Client message for store-and-forward for echoing unicast messages
client_message = None

# Boolean flag to check if connected to server
connected_to_server = False

# Emoji dict for bonus points :)
emoji_dict = {
    ":heart:": "<3",
    ":rat:": "<:3~",
    ":sad:": ":c",
    ":happy:": "c:",
    ":blush:": "૮ ˶ᵔ ᵕ ᵔ˶ ა",
    ":angel:":  "ପ(๑•ᴗ•๑)ଓ ♡",
    ":pout:": "૮₍ ˃ ⤙ ˂ ₎ა"
}


def replace_emojis(msg: list):
    for i in range(len(msg)):
        if msg[i] in emoji_dict:
            msg[i] = emoji_dict[msg[i]]

    return msg

# Main program logic
def send_to_server(cmd: str, handle: str = None, msg: str = None):
    global client_message
    
    # Build command object
    message = {
        "command": cmd
    }
    if handle is not None:
        message["handle"] = handle
    if msg is not None:
        message["message"] = msg
    
    client_message = message

    # Encode command object as string
    message_json = json.dumps(message)

    # Send JSON-encoded command to server
    try:
        client_sock.sendto(message_json.encode(), (server_addr, server_port))
    except:
        print("Error: Not yet connected to a server.")


def recv_from_server():
    global client_message, connected_to_server
    
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
                connected_to_server = True
            elif cmd == "leave":
                print("Connection closed. Thank you!")
                connected_to_server = False
            elif cmd == "register":
                print("Welcome {0}!".format(response["handle"]))
            elif cmd == "all":
                print("{0}: {1}".format(response["handle"], response["message"]))
            elif cmd == "msg":
                # Echo the sent message if the response is equal to the stored message
                if response == client_message:
                    print("[To {0}]: {1}".format(response["handle"], response["message"]))
                    client_message = None
                # Receiving a message from another client
                else:
                    print("[From {0}]: {1}".format(response["handle"], response["message"]))
            elif cmd == "error":
                print("Error: {0}".format(response["message"]))
        except:
            pass


def error_check(cmd: str, args: list) -> bool:
    # Error checking for command syntax
    if cmd not in ["/join", "/leave", "/register", "/all", "/msg", "/?", "/emojis"]:
        print("Error: Command not found.")
        return False

    # Checking errors for /join
    if cmd == "/join":
        if len(args) != 2 or not args[1].isdigit():
            print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
            return False
        else:
            try:
                socket.inet_aton(args[0])
            except:
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
    if cmd == "/register" and len(args) != 1:
        print("Error: Command parameters do not match or is not allowed.")
        return False

    # Checking errors for /all
    if cmd == "/all" and (len(args) < 1 or args[0] == ""):
        print("here1Error: Command parameters do not match or is not allowed.")
        return False

    # Checking errors for /msg
    if cmd == "/msg" and len(args) < 2:
        print("here2Error: Command parameters do not match or is not allowed.")
        return False

    # Checking errors for /?
    if cmd == "/?" and len(args) > 0:
        print("Error: Command parameters do not match or is not allowed.")
        return False

    return True

# Creating thread for receiving replies from server
recv_thread = threading.Thread(target = recv_from_server)
recv_thread.daemon = True
recv_thread.start()


# Main loop for receiving CLI input
while True:
    # Input from CLI
    try:
        client_message = input()
    except KeyboardInterrupt:
        try:
            send_to_server("leave")
        except:
            pass
        break
    client_cmdline = client_message.lstrip().split(" ")

    # Split command line into command and arguments
    client_cmd = client_cmdline[0]
    client_args = client_cmdline[1:]

    if client_cmd == "/all":
        try:
            client_args = replace_emojis(client_args)
            client_args[0] = ' '.join(client_args)
            client_args = [arg for i,arg in enumerate(client_args) if i==0] 
        except: 
            client_args = [""]
    elif client_cmd == "/msg":
        if len(client_args) >= 2:
            client_args = replace_emojis(client_args)
            client_args = list([client_args[0], " ".join(client_args[1:])])
        else:
            print("Error: Command parameters do not match or is not allowed.")
            continue

    # Check command line for errors
    if not error_check(client_cmd, client_args):
        continue

    # Parse commands
    if client_cmd == "/join":
        # Save server details
        server_addr = client_args[0]
        server_port = int(client_args[1])

        # Join server
        send_to_server('join')

        # Wait for join confirmation from server
        time.sleep(0.25)

        # If no received confirmation from server 
        if not connected_to_server:
            server_addr = None
            server_port = None
            print("Error: Server does not exist.")


    elif client_cmd == "/register":
        send_to_server("register", handle=client_args[0])
    elif client_cmd == "/all":
        send_to_server("all", msg=client_args[0])
    elif client_cmd == "/msg":
        send_to_server("msg", handle=client_args[0], msg=client_args[1])
    elif client_cmd == "/?":
        print("""
        
+---------------------------------------+------------------------------+-----------------------------+
|                Command                |        Input Syntax          |     Sample Input Script     |
+---------------------------------------+------------------------------+-----------------------------+
| Connect to a server                   | /join <server_ip_add> <port> | /join 127.0.0.1 12345       |
| Disconnect from the server            | /leave                       | /leave                      |
| Register a unique handle or alias     | /register <handle>           | /register Jacob             |
| Send a message to all users in server | /all <message>               | /all Everyone can see this. |
| Send a direct message to a user       | /msg <handle> <message>      | /msg Jacob Hello jacob.     |
| View commands                         | /?                           | /?                          |
| View emoji list                       | /emojis                      | /emojis                     |
+---------------------------------------+------------------------------+-----------------------------+


        """)
    elif client_cmd == "/emojis":
        print("""
        Insert the emojis into your message!
+---------+-------------+
| Command |    Emoji    |
+---------+-------------+
| :heart: | <3          |
| :rat:   | <:3~        |
| :sad:   | :c          |
| :happy: | c:          |
| :blush: | ૮ ˶ᵔ ᵕ ᵔ˶ ა |
| :angel: | ପ(๑•ᴗ•๑)ଓ ♡ |
| :pout:  | ૮₍ ˃ ⤙ ˂ ₎ა |
+---------+-------------+


        """)
    elif client_cmd == "/leave":
        # Delete connection details
        
        send_to_server("leave")
        server_addr = None
        server_port = None
