import socket
import struct
import threading
import time

# Server Configuration
MAGIC_COOKIE = 0xabcddcba
OFFER_MESSAGE_TYPE = 0x2
REQUEST_MESSAGE_TYPE = 0x3
PAYLOAD_MESSAGE_TYPE = 0x4
UDP_BROADCAST_PORT = 13117
UDP_LISTENER_PORT = 60000
TCP_PORT = 12345

class SpeedTestServer:
    def __init__(self):
        self.broadcast_socket = None
        self.listener_socket = None
        self.server_tcp_socket = None

        # Condition to make sure listening starts
        self.condition = threading.Condition()

    def start_udp_broadcast(self):
        """Broadcasts UDP offer messages every second."""
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print(f"Server started, listening on IP address {socket.gethostbyname(socket.gethostname())}")

        while True:
            message = struct.pack('!IBHH', MAGIC_COOKIE, OFFER_MESSAGE_TYPE, UDP_LISTENER_PORT, TCP_PORT)
            self.broadcast_socket.sendto(message, ('<broadcast>', UDP_BROADCAST_PORT))
            time.sleep(1)

    def handle_tcp_connection(self, client_socket):
        """Handles a single TCP client connection."""
        try:
            data = client_socket.recv(1024).decode()
            file_size = int(data.strip())
            payload = b'a' * file_size  # Generate file of requested size
            client_socket.sendall(payload)
        except Exception as e:
            print(f"Error handling TCP connection: {e}")
        finally:
            client_socket.close()

    def handle_udp_connection(self, client_address, request_data):
        """Handles a single UDP client request."""
        try:
            file_size = struct.unpack('!Q', request_data[5:13])[0]
            total_segments = (file_size + 1023) // 1024  # Assuming 1024-byte packets

            for segment in range(total_segments):
                payload = struct.pack(
                    '!IBQQ', MAGIC_COOKIE, PAYLOAD_MESSAGE_TYPE, total_segments, segment
                ) + b'a' * 1024
                self.listener_socket.sendto(payload, client_address)
                # print(f"Sending segment {segment + 1}/{total_segments} to {client_address}")
                time.sleep(0.000000000000000000000001)  # Add delay, helps so we wont drop packets

        except Exception as e:
            print(f"Error handling UDP connection: {e}")


    def start_tcp_listener(self):
        """Listens for TCP connections and spawns threads to handle them."""
        self.server_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow immediate reuse
        self.server_tcp_socket.bind(("", TCP_PORT))
        self.server_tcp_socket.listen(5)
        print("TCP server listening...")

        while True:
            client_socket, _ = self.server_tcp_socket.accept()
            threading.Thread(target=self.handle_tcp_connection, args=(client_socket,)).start()

    def start_udp_listener(self):
        """Listens for UDP requests and spawns threads to handle them."""

        # Opening socket for listening on a specific port (mainly had an issue with using the same computer to test)
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener_socket.bind(("", UDP_LISTENER_PORT))

        while True:
            try:
                data, addr = self.listener_socket.recvfrom(4096)
                print(f"Received UDP packet from {addr}, data length: {len(data)}")
                if len(data) >= 13:
                    cookie, message_type = struct.unpack('!IB', data[:5])
                    if cookie == MAGIC_COOKIE and message_type == REQUEST_MESSAGE_TYPE:
                        print(f"Dispatching UDP handler for {addr}")
                        threading.Thread(target=self.handle_udp_connection, args=(addr, data)).start()
            except Exception as e:
                print(f"Error receiving UDP data: {e}")

    def start(self):
        """Starts the server threads for broadcasting and handling requests."""
        udp_broadcast_thread = threading.Thread(target=self.start_udp_broadcast, daemon=True)
        udp_broadcast_thread.start()

        udp_listener_thread = threading.Thread(target=self.start_udp_listener, daemon=True)
        udp_listener_thread.start()

        self.start_tcp_listener()

if __name__ == "__main__":
    server = SpeedTestServer()
    server.start()
