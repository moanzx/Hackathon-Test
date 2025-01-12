import socket
import struct
import threading
import time

# Constants
MAGIC_COOKIE = 0xabcddcba  # To identify valid messages
MESSAGE_TYPE_OFFER = 0x2   # Specifies an offer message type
MESSAGE_TYPE_REQUEST = 0x3 # Specifies an request message type
UDP_PORT = 13117           # The port to listen for broadcasts

def create_UDP_socket():
    """
    Creates a UDP socket for broadcasting messages.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Creating the socket with the following parameters:
    # socket.AF_INET: IPv4
    # socket.SOCK_DGRAM: UDP communication (connectionless)

    # udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # # Setting up the socket configurations with the following parameters:
    # # socket.SOL_SOCKET: setting the socket with the "General behaivour" of a socket
    # # socket.SO_REUSEPORT: Allows multiple applications to bind to the same port
    # # 1: enables broadcasting

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
    print('Client started, listening for offer requests...')
    while True:
        data, addr = udp_socket.recvfrom(1024)  # Receive data from a broadcast message

        try:
            # Unpack the first 9 bytes of the offer message
            magic_cookie, msg_type, udp_port, tcp_port = struct.unpack('!I B H H', data[:9])
            #  Decodes the first 9 bytes of the message and sets them up in their variable

            # # Validate the message
            if magic_cookie == MAGIC_COOKIE and msg_type == 0x2:
                print(f"Received offer from {addr[0]}")
                return addr[0], udp_port # return the ip from where we recieved offer
            

        except struct.error:
            print(f"Received invalid message from {addr}")

def create_request_message(file_size):
    """
    Creates an offer message with the required format into easier data that the server can send information as.
    """
    message = struct.pack('!I B Q', MAGIC_COOKIE, MESSAGE_TYPE_REQUEST, file_size)

    # Constructing the message in the specific offer message format using binary encoding:
    # '!I B H H': setting up the format
    # !: specifies the byte order
    # I: Unsigned 4-byte Integer - MAGIC_COOKIE
    # B: Unsigned 1-byte Integer - MESSAGE_TYPE_OFFER
    # Q: Unsigned 8-byte integer - file_size
    return message


def send_udp_request(udp_socket, server_ip, port, file_size, index):

    request_message = create_request_message(file_size)
    udp_socket.sendto(request_message, (server_ip, port))
    print(f"sent udp number: {index}, to address: {server_ip}:{port}")

if __name__ == "__main__":

    # file_size = input("Please input file size: ")
    # tcp_connection_amount = input("Please TCP connections: ")
    # udp_connection_amoount = input("Please UDP connections: ")
    
    file_size = 8589934592 # 1GB = 1 * 8 * 2^30 = 8589934592
    tcp_connection_amount = 0
    udp_connection_amount = 2

    udp_packet_size = file_size // udp_connection_amount


    udp_socket = create_UDP_socket()
    offered_server_ip, offered_server_port = listen_for_offers(udp_socket)
    threads = []
    for i in range(tcp_connection_amount):
        pass # open thread for tcp connection

    
    for i in range(1, udp_connection_amount + 1):
        threads.append(threading.Thread(target=send_udp_request, args=(udp_socket, offered_server_ip, offered_server_port, udp_packet_size, i), daemon=True))
        threads[-1].start()

    for thread in threads:
        thread.join()

    while True:
        pass

    







