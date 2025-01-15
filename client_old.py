import socket
import struct
import threading
import time
import queue

# Constants
MAGIC_COOKIE = 0xabcddcba  # To identify valid messages
MESSAGE_TYPE_OFFER = 0x2   # Specifies an offer message type
MESSAGE_TYPE_REQUEST = 0x3 # Specifies an request message type
UDP_PORT = 13117           # The port to listen for broadcasts
MAX_SIZE_FOR_SEGMENT = 64000 # 
BUFFER_SIZE = 65535
segment_lock = threading.Lock()
segment_base = 0
message_queue = queue.Queue()


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
    process_messages(udp_socket, file_size)


def process_messages(udp_socket, file_size):
    """
    Listens for UDP broadcast offers and parses the offer message.
    """
    print('Client started, listening for offer payloads...')
    global segment_base
    total_segments_recieved = 0
    total_segments = -1
    total_chunks = (file_size + MAX_SIZE_FOR_SEGMENT - 1) // MAX_SIZE_FOR_SEGMENT
    seg_num_in_range = None

    with segment_lock:
        seg_num_in_range = segment_base
        segment_base += total_chunks

    while True:
        try:
            message = message_queue.get(timeout=2)
        except queue.Empty:
            print(f"Total received: {total_segments_recieved}/{total_segments if total_segments > 0 else '?'}")
            return

        data, addr = message
        try:
            magic_cookie, msg_type = struct.unpack('!I B', data[:5])
            if magic_cookie == MAGIC_COOKIE and msg_type == 0x4:
                magic_cookie, msg_type, temp_total_segments, segment_number = struct.unpack('!I B Q Q', data[:21])
                # print(f"Processing segment {segment_number}")

                if segment_number // total_chunks != seg_num_in_range // total_chunks:
                    # print(f"Segment {segment_number} not in range, returning to queue.")
                    message_queue.put(message)
                    continue

                total_segments = temp_total_segments
                total_segments_recieved += 1
                print(f"Received segment {segment_number}")
        except struct.error:
            print(f"Invalid message format from {addr}")


def listening_to_payloads(udp_socket):
    """
    Listens for UDP broadcast offers and parses the offer message.
    """
    print('Client started, listening for offer payloads...')
    recieve_time = None

    while True:
        try:
            data, addr = udp_socket.recvfrom(BUFFER_SIZE)
            if not message_queue.full():
                message_queue.put((data, addr))
            else:
                print("Message queue is full, dropping message.")
        except Exception as e:
            print(f"Error in listening_to_payloads: {e}")
            break

        if recieve_time:
            if time.time() - recieve_time  > 1:
                print("no packages for 1 sec finishing")
                return


if __name__ == "__main__":

    # file_size = input("Please input file size: ")
    # tcp_connection_amount = input("Please TCP connections: ")
    # udp_connection_amoount = input("Please UDP connections: ")
    
    # file_size = 8589934592 # 1GB = 1 * 8 * 2^30 = 8589934592
    file_size = 8589930 # 1GB = 1 * 8 * 2^30 = 8589934592
    tcp_connection_amount = 0
    udp_connection_amount = 4

    udp_packet_size = file_size // udp_connection_amount


    udp_socket = create_UDP_socket()
    offered_server_ip, offered_server_port = listen_for_offers(udp_socket)
    threads = []
    for i in range(tcp_connection_amount):
        pass # open thread for tcp connection

    
    udp_start = time.time()
    for i in range(1, udp_connection_amount + 1):
        threads.append(threading.Thread(target=send_udp_request, args=(udp_socket, offered_server_ip, offered_server_port, udp_packet_size, i), daemon=True))
        threads[-1].start()


    threads.append(threading.Thread(target=listening_to_payloads, args=(udp_socket,), daemon=True))
    threads[-1].start()

    for thread in threads:
        thread.join()



    while True:
        pass

    







