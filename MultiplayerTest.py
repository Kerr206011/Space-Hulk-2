import socket
import threading

class Server:
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.PORT = 5000
        self.threadingBool = True       
        self.clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(5)
        print(f"Server listening on {self.HOST}:{self.PORT}")
        self.player1 = None
        self.player2 = None
        self.activePlayer = None

    def handle_client(self, client_socket):
        while self.threadingBool:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                if client_socket == self.activePlayer:
                    print(f"Received: {data.decode()}")
                    for client in self.clients:
                        client.send(data)
            except:
                break
        self.clients.remove(client_socket)
        client_socket.close()

    def accept_clients(self):
        while self.threadingBool:
            client_socket, addr = self.server.accept()
            print(f"Client connected: {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            
            if self.player1 == None:
                self.player1 = client_socket
            else:
                self.player2 = client_socket

    def command_listener(self):
        while self.threadingBool:
            cmd = input("Enter Command: ")
            if cmd.lower() == "quit":
                print("Shutting down server...")
                self.threadingBool = False
                self.server.close()
                break
            
            elif cmd.lower() == "1":
                self.activePlayer = self.player1

    def start_server(self):
        threading.Thread(target=self.accept_clients, daemon=True).start()
        self.command_listener()

server = Server()
server.start_server()