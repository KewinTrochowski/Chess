import socket

def create_tcp_client(server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_host, server_port))
        print(f"Connected with {server_host} on port {server_port}")
        return client_socket
    except ConnectionRefusedError:
        print(f"Cannot connect with {server_host}:{server_port}.")
        return None
def send_message_to_tcp_server(client_socket, message):
    if client_socket is not None and message:
        client_socket.sendall(message.encode())
        print("Message send:", message)


"""
if __name__ == '__main__':
    HOST = '127.0.0.1' 
    PORT = 55555  
    client_socket = create_tcp_client(HOST, PORT)
    if client_socket:
        try:
            while True:
                message = input("Wpisz wiadomość do wysłania (wpisz 'exit' aby zakończyć): ")
                if message.lower() == 'exit':
                    break
                send_message_to_tcp_server(client_socket, message)
        finally:
            client_socket.close()
            print("Rozłączono z serwerem.")
"""