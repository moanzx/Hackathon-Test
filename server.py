import socket
import struct
import time

# Constants
MAGIC_COOKIE = 0xabcddcba  # Identifies valid messages
MESSAGE_TYPE_OFFER = 0x2   # Specifies an "offer" message type
UDP_PORT = 13117           # Port for broadcasting messages
TCP_PORT = 12345           # Port for incoming TCP connections

def create_UDP_socket():
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
    while True:
        udp_socket.sendto(message, ('<broadcast>', UDP_PORT))  # Send to broadcast address
        # udp_socket.sendto(data, (host, port))
        # <broadcast>: is a special address used to send data to all devices on the network
        # UDP_PORT: we use the UDP_PORT because broadcasting and the client listens on UDP
        print("Broadcasting offer...")
        time.sleep(1)  # Wait 1 second before broadcasting again


u = create_UDP_socket()
m = create_offer_message()
broadcast_offers(u, m)