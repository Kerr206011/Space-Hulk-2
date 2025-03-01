import socket
import threading

class Server:
    def __init__(self):
        # Server setup
        self.HOST = '127.0.0.1'  # Change to your public IP for Internet play
        self.PORT = 5000
        self.threadingBool = True       
        # Store connected clients
        self.clients = []
        player1 = None
        player2 = None
        activePlayer = player1

    def handle_client(self, client_socket):
        while self.threadingBool:
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

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen(5)
        print(f"Server listening on {self.HOST}:{self.PORT}")
        while True:
            cmd = input("Enter Command: ")
            if cmd == "quit":
                threadingBool = False
                break
            client_socket, addr = server.accept()
            print(f"Client connected: {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

server = Server()
server.start_server()