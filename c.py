import socket
import struct
import threading
import time

# Client Configuration
MAGIC_COOKIE = 0xabcddcba
OFFER_MESSAGE_TYPE = 0x2
REQUEST_MESSAGE_TYPE = 0x3
PAYLOAD_MESSAGE_TYPE = 0x4
UDP_BROADCAST_PORT = 13117
BUFFER_SIZE = 4096

class SpeedTestClient:
    def __init__(self):
        self.udp_socket = None
        self.server_address = None

    def listen_for_offers(self):
        """Listens for server offer messages via UDP broadcast."""
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(("", UDP_BROADCAST_PORT))
        print("Client started, listening for offer requests...")

        while True:
            data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            if len(data) >= 9:
                cookie, message_type = struct.unpack('!IB', data[:5])
                if cookie == MAGIC_COOKIE and message_type == OFFER_MESSAGE_TYPE:
                    udp_port, tcp_port = struct.unpack('!HH', data[5:9])
                    self.server_address = (addr[0], udp_port, tcp_port)
                    print(f"Received offer from {addr[0]}")
                    return

    def send_udp_request(self, file_size, index):
        """Sends a UDP request to the server and measures the speed."""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.settimeout(1)  # Independent socket per thread

        udp_port = self.server_address[1]
        server_udp_address = (self.server_address[0], udp_port)

        request_packet = struct.pack('!IBQ', MAGIC_COOKIE, REQUEST_MESSAGE_TYPE, file_size)
        udp_socket.sendto(request_packet, server_udp_address)

        start_time = time.time()
        total_bytes = 0
        received_segments = []
        total_segments = None  # To be updated when the first packet is received

        while True:
            try:
                data, _ = udp_socket.recvfrom(BUFFER_SIZE)

                if len(data) > 20:
                    cookie, message_type, total_segments_in_packet, segment_number = struct.unpack('!IBQQ', data[:21])
                    if cookie == MAGIC_COOKIE and message_type == PAYLOAD_MESSAGE_TYPE:
                        if total_segments is None:
                            total_segments = total_segments_in_packet  # Set total segments from the first packet
                        total_bytes += len(data) - 21
                        received_segments.append(segment_number)
                        # print(f"Received segment {segment_number + 1}/{total_segments_in_packet}")
            except socket.timeout:
                break

        elapsed_time = time.time() - start_time
        udp_socket.close()

        received_percentage = (len(received_segments) / total_segments * 100) if total_segments else 0
        speed = (total_bytes * 8 / elapsed_time) if elapsed_time > 0 else 0

        print(f"UDP transfer #{index} finished, total time: {elapsed_time:.2f} seconds, "
              f"speed: {speed:.2f} bits/second, percentage received: {received_percentage:.2f}%")

    def send_tcp_request(self, file_size, index):
        """Sends a TCP request to the server and measures the speed."""
        tcp_port = self.server_address[2]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.server_address[0], tcp_port))
            tcp_socket.sendall(f"{file_size}\n".encode())

            start_time = time.time()
            total_bytes = 0

            while True:
                data = tcp_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                total_bytes += len(data)

            elapsed_time = time.time() - start_time
            if not elapsed_time:
                print(f"TCP transfer #{index} finished, total time: {elapsed_time:.2f} seconds, speed: too fast to calculate")
            else:
                print(f"TCP transfer #{index} finished, total time: {elapsed_time:.2f} seconds, speed: {total_bytes * 8 / elapsed_time:.2f} bits/second")

    def start(self):
        """Starts the client application."""
        file_size = int(input("Enter file size (bytes): "))
        tcp_connections = int(input("Enter number of TCP connections: "))
        udp_connections = int(input("Enter number of UDP connections: "))

        self.listen_for_offers()

        threads = []

        # Start TCP threads
        for i in range(1, tcp_connections + 1):
            thread = threading.Thread(target=self.send_tcp_request, args=(file_size, i))
            threads.append(thread)
            thread.start()

        # Start UDP threads
        for i in range(1, udp_connections + 1):
            thread = threading.Thread(target=self.send_udp_request, args=(file_size, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print("All transfers complete, listening to offer requests...")
        self.start()

if __name__ == "__main__":
    client = SpeedTestClient()
    client.start()
