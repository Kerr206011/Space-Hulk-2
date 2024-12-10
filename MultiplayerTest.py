#import Gamestates
import socket
import threading

# Server setup
HOST = '127.0.0.1'  # Change to your public IP for Internet play
PORT = 5000

# Store connected clients
clients = []

def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)  # Receive data
            if not data:
                break
            print(f"Received: {data.decode()}")
            # Echo data back to all clients
            for client in clients:
                client.send(data)
        except:
            break
    clients.remove(client_socket)
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        client_socket, addr = server.accept()
        print(f"Client connected: {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,)).start()

start_server()