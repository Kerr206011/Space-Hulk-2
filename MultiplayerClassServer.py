import socket
import threading
from MultiplayerClassClient import *

class Server:
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.PORT = 5000    
        self.clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(5)
        print(f"Server listening on {self.HOST}:{self.PORT}")
        self.player1 = None
        self.player2 = None
        self.activePlayer = None
        self.map = []

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                #if client_socket == self.activePlayer:
                else:
                    print(f"Received: {data.decode()}")
                    for client in self.clients:
                        client.send(data)
            except:
                break
        print(f"Client {client_socket} disconnected.")
        self.clients.remove(client_socket)
        client_socket.close()

    def accept_clients(self):
        a = 1
        while True:
            client_socket, addr = self.server.accept()
            print(f"Client connected: {addr}")
            print(a)
            a+=1
            self.sendSetupData("Level_1", client_socket)
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def command_listener(self):
        threadingBool = True
        while threadingBool:
            cmd = input("Enter Command: ")
            if cmd.lower() == "quit":
                print("Shutting down server...")
                threadingBool = False
                self.server.close()
                break
            
            elif cmd.lower() == "1":
                self.activePlayer = self.player1

    def load_map(self, levelFile):
        file_path = "Levels/"+levelFile+".json"
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        bluePrint = data["map"]

        for entry in bluePrint:

            if entry[1] == "tile":
                newTile = Tile(entry[2], entry[4], entry[0][0],entry[0][1],entry[3])
                self.map.append(newTile)

            elif entry[1] == "door":
                newDoor = Door(entry[2], entry[4], entry[6], entry[0][0], entry[0][1], entry[3], entry[5])
                if entry[5] == False:
                    newDoor.change_picture(newDoor.pictureClosedPath)
                self.map.append(newDoor)

            elif entry[1] == "wall":
                newWall = Wall(entry[2],entry[0][0],entry[0][1])
                self.map.append(newWall)

            elif entry[1] == "entry":
                newEntry = EntryPoint(entry[2],entry[0][0],entry[0][1],entry[3])
                self.map.append(newEntry)

            elif entry[1] == "control":
                newControl = ControlledArea(entry[2],entry[4],entry[0][0],entry[0][1],entry[3])
                self.map.append(newControl)

        print(self.map)

    def sendSetupData(self, levelFile, client):
        file_path = "Levels/"+levelFile+".json"
        data = {"purpose": "setup",
                "mapFile":file_path}
        client.send(json.dumps(data).encode())

    def start_server(self):
        self.load_map("Level_1")
        threading.Thread(target=self.accept_clients, daemon=True).start()
        #self.command_listener()

    def sendPlayer1Update(self):
        pass

server = Server()
client = Client()
server.start_server()
client.start()