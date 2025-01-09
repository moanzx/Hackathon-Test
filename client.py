import socket
import struct

# Constants
MAGIC_COOKIE = 0xabcddcba  # To identify valid messages
MESSAGE_TYPE_OFFER = 0x2   # Specifies an offer message type
UDP_PORT = 13117           # The port to listen for broadcasts

def create_UDP_socket():
    """
    Creates a UDP socket for broadcasting messages.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Creating the socket with the following parameters:
    # socket.AF_INET: IPv4
    # socket.SOCK_DGRAM: UDP communication (connectionless)

    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Setting up the socket configurations with the following parameters:
    # socket.SOL_SOCKET: setting the socket with the "General behaivour" of a socket
    # socket.SO_REUSEPORT: Allows multiple applications to bind to the same port
    # 1: enables broadcasting

    udp_socket.bind(('', UDP_PORT))
    # Associating the socket with a specific IP address and port on the local machine:
    # The tuple is (host, port)
    # '': Bind to all available network interfaces on the machine (e.g., Wi-Fi, Ethernet)
    # UDP_PORT: Binds the socket to the UDP port

    return udp_socket

def connect_to_server(server_ip, tcp_port):
    """
    Connects to the server using TCP and establishes a basic connection.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            # Created a TCP socket with SOCK_STREAM (IPv4)
            tcp_socket.connect((server_ip, tcp_port))
            # the client to connect to the server using the provided server_ip and tcp_port, doing the handshake
            print(f"Connected to server {server_ip} on TCP port {tcp_port}")
    except Exception as e:
        print(f"Error connecting to server: {e}")


def listen_for_offers(udp_socket):
    """
    Listens for UDP broadcast offers and parses the offer message.
    """
    while True:
        data, addr = udp_socket.recvfrom(1024)  # Receive data from a broadcast message

        try:
            # Unpack the first 9 bytes of the offer message
            magic_cookie, msg_type, udp_port, tcp_port = struct.unpack('!I B H H', data[:9])
            #  Decodes the first 9 bytes of the message and sets them up in their variable

            # Validate the message
            if magic_cookie == MAGIC_COOKIE and msg_type == MESSAGE_TYPE_OFFER:
                print(f"Received offer from {addr[0]}: UDP port {udp_port}, TCP port {tcp_port}")
                connect_to_server(addr[0], tcp_port)
        except struct.error:
            print(f"Received invalid message from {addr}")

    

if __name__ == "__main__":
    udp_socket = create_UDP_socket()
    listen_for_offers(udp_socket)