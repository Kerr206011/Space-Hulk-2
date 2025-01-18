#import Gamestates
import socket
import threading

# Server setup
HOST = '127.0.0.1'  # Change to your public IP for Internet play
PORT = 5000

# # Store connected clients
# clients = []

# def handle_client(client_socket):
#     while True:
#         try:
#             data = client_socket.recv(1024)  # Receive data
#             if not data:
#                 break
#             print(f"Received: {data.decode()}")
#             # Echo data back to all clients
#             for client in clients:
#                 client.send(data)
#         except:
#             break
#     clients.remove(client_socket)
#     client_socket.close()

# def start_server():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((HOST, PORT))
#     server.listen(5)
#     print(f"Server listening on {HOST}:{PORT}")
#     while True:
#         client_socket, addr = server.accept()
#         print(f"Client connected: {addr}")
#         clients.append(client_socket)
#         threading.Thread(target=handle_client, args=(client_socket,)).start()

# start_server()

class Server:

    def __init__(self, HOST, PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))  
        # game = Game()
        # screen = pygame.display.set_mode((900.900))
        # self.gameStateManager = GameStateManager(game, screen)
        self.clients = []

    def run_server(self):
        self.server.listen(5)
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            client_socket, addr = self.server.accept()
            print(f"Client connected: {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,self,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)  # Receive data
                if not data:
                    break
                print(f"Received: {data.decode()}")
                # Echo data back to all clients
                for client in self.clients:
                    client.send(data)
            except:
                break
        self.clients.remove(client_socket)
        client_socket.close()

server = Server(HOST, PORT)
server.run_server()