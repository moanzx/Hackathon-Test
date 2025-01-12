import socket
import struct
import time
import threading

# Constants
MAGIC_COOKIE = 0xabcddcba  # Identifies valid messages
MESSAGE_TYPE_OFFER = 0x2   # Specifies an "offer" message type
MESSAGE_TYPE_REQUEST = 0x3 # Specifies a "request" message type
UDP_PORT = 13117           # Port for broadcasting messages
TCP_PORT = 12345           # Port for incoming TCP connections

def create_broadcasting_socket():
    """
    Creates a UDP socket for broadcasting messages.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Creating the socket with the following parameters:
    # socket.AF_INET: IPv4
    # socket.SOCK_DGRAM: UDP communication (connectionless)

    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Setting up the socket configurations with the following parameters:
    # socket.SOL_SOCKET: setting the socket with the "General behaivour" of a socket
    # socket.SO_BROADCAST: enabling the *ability* to send broadcast messages using this socket
    # 1: enables broadcasting
    # There are more configurations that can be set if we think we need this in Noam's notes

    udp_socket.bind(('', 0))
    # Associating the socket with a specific IP address and port on the local machine:
    # The tuple is (host, port)
    # '': Bind to all available network interfaces on the machine (e.g., Wi-Fi, Ethernet)
    # 0: port 0 means let the operating system assign an available port automatically

    return udp_socket

def create_udp_listening_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(('192.168.56.1', UDP_PORT))  # Listen on the specific port
    return udp_socket


def create_offer_message():
    """
    Creates an offer message with the required format into easier data that the server can send information as.
    """
    message = struct.pack('!I B H H', MAGIC_COOKIE, MESSAGE_TYPE_OFFER, UDP_PORT, TCP_PORT)

    # Constructing the message in the specific offer message format using binary encoding:
    # '!I B H H': setting up the format
    # !: specifies the byte order
    # I: Unsigned 4-byte Integer - MAGIC_COOKIE
    # B: Unsigned 1-byte Integer - MESSAGE_TYPE_OFFER
    # H: Unsigned 2-byte Integer Ports are in the range 0-65535, which fits into 2 bytes for both UDP, TCP
    return message


def broadcast_offers(udp_socket, message):
    """
    Continuously broadcasts the offer message.
    """
    print(f"Server started, listening on IP address {udp_socket.getsockname()[0]}")
    while True:
        udp_socket.sendto(message, ('<broadcast>', UDP_PORT))  # Send to broadcast address
        # udp_socket.sendto(data, (host, port))
        # <broadcast>: is a special address used to send data to all devices on the network
        # UDP_PORT: we use the UDP_PORT because broadcasting and the client listens on UDP

        time.sleep(1)  # Wait 1 second before broadcasting again

def handle_tcp_client(client_socket):
    """
    Handles a TCP client connection.
    """
    print("TCP client connected")
    try:
        while True:
            pass
    except Exception as e:
        print(f"Error handling TCP client: {e}")
    finally:
        client_socket.close()
        print("TCP client disconnected")


def handle_udp_requests(udp_socket):
    # print("Server listening for UDP requests...")
    # while True:
    #     try:
    #         data, addr = udp_socket.recvfrom(1024)  # Buffer size of 1024 bytes
    #         magic_cookie, message_type, file_size = struct.unpack('!I B Q', data[:13])
    #         if magic_cookie == MAGIC_COOKIE and message_type == MESSAGE_TYPE_REQUEST:
    #             print(f"Received valid request from {addr} with file size: {file_size}")
    #             # Optional response to the client
    #             response = f"Request received for file size: {file_size}".encode()
    #             udp_socket.sendto(response, addr)
    #     except struct.error:
    #         print("Received invalid message")
    #     except Exception as e:
    #         print(f"Error handling UDP request: {e}")
    print("Server listening for UDP requests...")
    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)
            if addr[0] == udp_socket.getsockname()[0]:
                # Ignore packets from the server itself
                continue
            print(data)
            if len(data) < 13:
                print(f"Invalid packet size from {addr}")
                continue
            magic_cookie, message_type, file_size = struct.unpack('!I B Q', data[:13])
            if magic_cookie == MAGIC_COOKIE and message_type == MESSAGE_TYPE_REQUEST:
                print(f"Received valid request from {addr} with file size: {file_size}")
                response = f"Request received for file size: {file_size}".encode()
                udp_socket.sendto(response, addr)
            else:
                print(f"Invalid magic cookie or message type from {addr}")
        except struct.error as e:
            print(f"Struct error: {e} from {addr}")
        except Exception as e:
            print(f"Error handling UDP request: {e}")



if __name__ == "__main__":
    # Create UDP socket and offer message
    broadcasting_socket = create_broadcasting_socket()
    listening_udp_socket = create_udp_listening_socket()
    message = create_offer_message()

    threading.Thread(target=broadcast_offers, args=(broadcasting_socket, message), daemon=True).start()
    threading.Thread(target=handle_udp_requests, args=(listening_udp_socket,), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server shutting down.")


    # while True:
    #     pass

    # # Set up TCP server
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
    #     tcp_socket.bind(('', TCP_PORT))
    #     tcp_socket.listen()
    #     print(f"Server listening on TCP port {TCP_PORT}")

    #     # Accept and handle TCP connections
    #     while True:
    #         client_socket, client_address = tcp_socket.accept()
    #         print(f"Accepted connection from {client_address}")
    #         threading.Thread(target=handle_tcp_client, args=(client_socket,), daemon=True).start()
