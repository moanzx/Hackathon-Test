import socket

UDP_PORT = 13117  # The port where the server is broadcasting

def listen_for_broadcasts():
    """
    Listens for UDP broadcasts on the specified port.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the address
        s.bind(('', UDP_PORT))  # Bind to all network interfaces on the specified port
        print(f"Listening for broadcasts on UDP port {UDP_PORT}...")

        while True:
            data, addr = s.recvfrom(1024)  # Receive up to 1024 bytes
            print(f"Received data: {data} from {addr}")

if __name__ == "__main__":
    listen_for_broadcasts()
