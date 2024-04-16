import socket
import threading
import sys

# List to keep track of connected clients
clients = []

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def handle_client_connection(self, client_socket, client_address):
        print(f'New connection from {client_address}')
        # Add the new client to the global list
        clients.append(client_socket)

        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                print(f'Received message from {client_address}: {message.decode()}')
                # Broadcast the message to all other clients
                self.broadcast_message(message, client_socket)
            except ConnectionResetError:
                break
        # Remove client from list and close the connection
        clients.remove(client_socket)
        client_socket.close()
        print(f'Connection with {client_address} has been closed.')

    def broadcast_message(self, message, sender_socket):
        """Send a received message to all other connected clients."""
        for client in clients:
            if client is not sender_socket:
                try:
                    client.sendall(message)
                except Exception as e:
                    print(f"Error sending message to {client.getpeername()}: {e}")

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f'Server listening at {self.host}:{self.port}')

        try:
            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client_connection, args=(client_socket, client_address))
                client_thread.start()
        except KeyboardInterrupt:
            print('Shutting down the server...')
        finally:
            # Close all client sockets
            for client in clients:
                client.close()
            server_socket.close()

if __name__ == '__main__':
    # get ip and port from command line arguments
    ip = sys.argv[1]
    port = int(sys.argv[2])

    server = Server(ip, port)
    server.start_server()