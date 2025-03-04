import socket
import threading

class Client:
    def __init__(self, host='127.0.0.1', port=5000):
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen_to_server(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                print(f"\nServer: {data.decode()}\nEnter message: ", end="", flush=True)
            except:
                break

    def start(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            threading.Thread(target=self.listen_to_server, daemon=True).start()
            while True:
                msg = input("Enter message: ")
                if msg.lower() == "quit":
                    break
                self.client_socket.send(msg.encode())
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()
            print("Disconnected from server.")

client = Client()
client.start()