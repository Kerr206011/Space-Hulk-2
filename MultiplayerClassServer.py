import socket
import threading
import json
from enum import Enum

class GameRole(Enum):
    SPECTATOR = "spectator"
    SPACEMARINE = "spacemarine"
    GENSTEALER = "genstealer"

class Server:
    def __init__(self, host="0.0.0.0", port=5000, discovery_port=5001):
        self.discovery_port = discovery_port
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []  # [(conn, addr, name, roll), ...]
        self.GSplayer = None
        self.SMplayer = None
        self.spectators  = []
        self.server_host = None

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        threading.Thread(target=self.accept_clients, args=()).start()
        threading.Thread(target=self.broadcast_listener, daemon=True).start()
        print("Server started")

    def accept_clients(self):
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        name = None
        print(f"New connection: {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())

                if message["purpose"] == "join_lobby":
                    name = message["name"]
                    if self.server_host == None:
                        self.server_host = {"conn":conn, "addr":addr, "name":name, "role":GameRole.SPECTATOR}
                        # print(self.server_host[2])
                    self.clients.append({"conn":conn, "addr":addr, "name":name, "role":GameRole.SPECTATOR})
                    self.spectators.append({"conn":conn, "addr":addr, "name":name, "role":GameRole.SPECTATOR})
                    self.send_lobby_update()

                    # Bestätigung an den neuen Client
                    self.send(conn, {
                        "purpose": "lobby_joined",
                        "players": [(c["name"],c["role"].name) for c in self.clients]
                    })
                
                elif message["purpose"] == "rolechange":
                    if message["role"] == "genstealer":
                        if self.GSplayer == None:
                            if self.SMplayer != None:
                                if self.SMplayer["conn"] == conn and self.SMplayer["addr"] == addr and self.SMplayer["name"] == name:
                                    self.SMplayer = None
                            for player in self.clients:
                                if player["conn"] == conn and player["addr"] == addr and player["name"] == name:
                                    player["role"] = GameRole.GENSTEALER
                            self.GSplayer = {
                                "conn": conn,
                                "addr": addr,
                                "name": name,
                                "role": GameRole.GENSTEALER
                            }
                            print("gs selected!")
                            message = {"purpose" : "rolechange",
                                       "role" : self.GSplayer["role"].name}
                            self.send(conn, message)
                            self.send_lobby_update()

                    elif message["role"] == "spacemarine":
                        if self.SMplayer == None:
                            if self.GSplayer != None:
                                if self.GSplayer["conn"] == conn and self.GSplayer["addr"] == addr and self.GSplayer["name"] == name:
                                    self.GSplayer = None
                            for player in self.clients:
                                if player["conn"] == conn and player["addr"] == addr and player["name"] == name:
                                    player["role"] = GameRole.SPACEMARINE
                            self.SMplayer = {
                                "conn": conn,
                                "addr": addr,
                                "name": name,
                                "role": GameRole.SPACEMARINE
                            }
                            message = {"purpose" : "rolechange",
                                       "role" : self.SMplayer["role"].name}
                            self.send(conn, message)
                            print("sm selected!")
                            self.send_lobby_update()
                    
                    else:
                        if self.GSplayer != None:
                            if self.GSplayer["conn"] == conn and self.GSplayer["addr"] == addr and self.GSplayer["name"] == name:
                                    self.GSplayer = None
                        if self.SMplayer != None:
                            if self.SMplayer["conn"] == conn and self.SMplayer["addr"] == addr and self.SMplayer["name"] == name:
                                    self.SMplayer = None
                        for player in self.clients:
                                if player["conn"] == conn and player["addr"] == addr and player["name"] == name:
                                    player["role"] = GameRole.SPECTATOR
                        message = {"purpose" : "rolechange",
                                    "role" : GameRole.SPECTATOR.name}
                        self.send(conn, message)
                        print("back to spectator!")
                        self.send_lobby_update()

                if message["purpose"] == "disconnect":
                    break

        except Exception as e:
            print(f"Error with {addr}: {e}")
        finally:
            conn.close()
            if conn:
                self.clients = [c for c in self.clients if c["conn"] != conn]
                self.send_lobby_update()

    def send(self, conn, message):
        conn.sendall(json.dumps(message).encode())

    def send_lobby_update(self):
        players = [(c["name"], c["role"].name) for c in self.clients]
        for c in self.clients:
            self.send(c["conn"], {
                "purpose": "lobby_update",
                "players": players,
            })

    def broadcast_listener(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(("", self.discovery_port))

        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                if data.decode() == "DISCOVER_SPACEHULK":
                    response = f"SPACEHULK_SERVER:{self.port}"
                    udp_socket.sendto(response.encode(), addr)
            except Exception as e:
                print("Discovery error:", e)

# class Test_Server:
#     def __init__(self):
#         self.HOST = '127.0.0.1'
#         self.PORT = 5000
#     def __init__(self):
#         self.HOST = '127.0.0.1'
#         self.PORT = 5000    
#         self.clients = []
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.bind((self.HOST, self.PORT))
#         self.server.listen(5)
#         print(f"Server listening on {self.HOST}:{self.PORT}")
#         self.player_G = None
#         self.player_S = None
#         self.activePlayer = None
#         self.map = []
#         self.selectedTile_s = None
#         self.clickedTile_s = None
#         self.selectedTile_g = None
#         self.clickedTile_g = None
#         self.current_gameState = "Setup"
#         self.SMModelList = []
#         self.GSModelList = []
#         self.BLModelList = []

#     def handle_client(self, client_socket):
#         while True:
#             try:
#                 data = client_socket.recv(1024)
#                 if not data:
#                     break
#                 #if client_socket == self.activePlayer:
#                 else:
#                     print(f"Received: {data.decode()}")
#                     message = json.loads(data.decode())
#                     if message["purpose"] == "clicked":
#                         for tile in self.map:
#                             if tile.x == message["tile"][0] and tile.y == message["tile"][1]:
#                                 if client_socket == self.player_S:
#                                     if isinstance(tile, Tile):
#                                         if tile.isOccupied == False or not isinstance(tile.occupand, SpaceMarine):
#                                             self.clickedTile_s = tile
#                                             self.send_confirmation(True, "clicked", self.player_S)
#                                 elif client_socket == self.player_G:
#                                     if isinstance(tile, Tile):
#                                         if tile.isOccupied == False or isinstance(tile.occupand, SpaceMarine):
#                                             self.clickedTile_s = tile
#                                             self.send_confirmation(True, "clicked", self.player_G)
#             except:
#                 break
            
#         print(f"Client {client_socket} disconnected.")
#         self.clients.remove(client_socket)
#         client_socket.close()

#     def accept_clients(self):
#         a = 1
#         while a < 3:
#             client_socket, addr = self.server.accept()
#             print(f"Client connected: {addr}")
#             print(a)
#             a+=1
#             self.sendSetupData("Level_1", client_socket)
#             self.clients.append(client_socket)
#             if a == 2:
#                 self.player_S = client_socket
#                 self.sendRole("S", self.player_S)
#             else:
#                 self.player_G = client_socket
#                 self.sendRole("G", self.player_G)
#             threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

#     def command_listener(self):
#         threadingBool = True
#         while threadingBool:
#             cmd = input("Enter Command: ")
#             if cmd.lower() == "quit":
#                 print("Shutting down server...")
#                 threadingBool = False
#                 self.server.close()
#                 break
            
#             elif cmd.lower() == "1":
#                 self.activePlayer = self.player1

#     def send_confirmation(self, conf:bool, target:str, client):
#         data = {"purpose" : "confirmation",
#                 "target" : target,
#                 "confirmation" : conf}
#         client.send(json.dumps(data).encode())

#     def load_map(self, levelFile):
#         file_path = "Levels/"+levelFile+".json"
#         with open(file_path, 'r') as json_file:
#             data = json.load(json_file)

#         bluePrint = data["map"]

#         for entry in bluePrint:

#             if entry[1] == "tile":
#                 newTile = Tile(entry[2], entry[4], entry[0][0],entry[0][1],entry[3])
#                 self.map.append(newTile)

#             elif entry[1] == "door":
#                 newDoor = Door(entry[2], entry[4], entry[6], entry[0][0], entry[0][1], entry[3], entry[5])
#                 if entry[5] == False:
#                     newDoor.change_picture(newDoor.pictureClosedPath)
#                 self.map.append(newDoor)

#             elif entry[1] == "wall":
#                 newWall = Wall(entry[2],entry[0][0],entry[0][1])
#                 self.map.append(newWall)

#             elif entry[1] == "entry":
#                 newEntry = EntryPoint(entry[2],entry[0][0],entry[0][1],entry[3])
#                 self.map.append(newEntry)

#             elif entry[1] == "control":
#                 newControl = ControlledArea(entry[2],entry[4],entry[0][0],entry[0][1],entry[3])
#                 self.map.append(newControl)

#     def sendSetupData(self, levelFile, client):
#         file_path = "Levels/"+levelFile+".json"
#         data = {"purpose": "setup",
#                 "mapFile":file_path}
#         client.send(json.dumps(data).encode())

#     def sendRole(self, role, client):
#         data = {"purpose" : "role",
#                 "role" : role}
#         client.send(json.dumps(data).encode())

#     def start_server(self):
#         self.load_map("Level_1")
#         threading.Thread(target=self.accept_clients, daemon=True).start()

#     def sendPlayer1Update(self):
#         pass

#     def handle_lobby(self):
#         pass

# class Server:

#     def __init__(self):
#         self.HOST = '127.0.0.1'
#         self.PORT = 5000    
#         self.clients = []
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.bind((self.HOST, self.PORT))
#         self.server.listen(5)
#         print(f"Server listening on {self.HOST}:{self.PORT}")
#         self.players_G = []
#         self.players_S = []
#         self.activePlayer = None
#         self.admin = None
#         self.map = []
#         self.current_gameState = "Setup"
#         self.gsready = False
#         self.smready = False
#         self.SMModelList = []
#         self.GSModelList = []
#         self.BLModelList = []

#     def handle_client(self, client_socket):
#         while True:
#             try:
#                 data = client_socket.recv(1024)
#                 if not data:
#                     break
#                 #if client_socket == self.activePlayer:
#                 else:
#                     print(f"Received: {data.decode()}")
#                     message = json.loads(data.decode())
#                     if message["purpose"] == "clicked":
#                         for tile in self.map:
#                             if tile.x == message["tile"][0] and tile.y == message["tile"][1]:
#                                 if client_socket == self.player_S:
#                                     if isinstance(tile, Tile):
#                                         if tile.isOccupied == False or not isinstance(tile.occupand, SpaceMarine):
#                                             self.clickedTile_s = tile
#                                             self.send_confirmation(True, "clicked", self.player_S)
#                                 elif client_socket == self.player_G:
#                                     if isinstance(tile, Tile):
#                                         if tile.isOccupied == False or isinstance(tile.occupand, SpaceMarine):
#                                             self.clickedTile_s = tile
#                                             self.send_confirmation(True, "clicked", self.player_G)

#                     # elif message["purpose"] == "ready":
#                     #     if client_socket == self.player_S:
#                     #         self.smready = not self.smready
#                     #     elif client_socket == self.player_G:
#                     #         self.gsready = not self.gsready

#                     elif message["purpose"] == "roleswitch":
#                         if message["new_role"] == "gs":
#                             if client_socket not in self.players_G:
#                                 self.players_G.append(client_socket)
                            
#                             if client_socket in self.players_S:
#                                 self.players_S.remove(client_socket)

#                         elif message["new_role"] == "sm":
#                             if client_socket not in self.players_S:
#                                 self.players_S.append(client_socket)
                            
#                             if client_socket in self.players_G:
#                                 self.players_G.remove(client_socket)

#                         else:
#                             if client_socket in self.players_G:
#                                 self.players_G.remove(client_socket)
#                             if client_socket in self.player_S:
#                                 self.players_G.remove(client_socket)

                        
#             except:
#                 break
            
#         print(f"Client {client_socket} disconnected.")
#         self.clients.remove(client_socket)
#         client_socket.close()

#     def accept_clients(self):
#         a = 1
#         while a < 3:
#             client_socket, addr = self.server.accept()
#             print(f"Client connected: {addr}")
#             print(a)
#             a+=1
#             self.sendSetupData("Level_1", client_socket)
#             self.clients.append(client_socket)
#             if a == 2:
#                 self.admin = client_socket
#                 self.player_S = client_socket
#                 self.sendRole("S", self.player_S)
#             else:
#                 self.player_G = client_socket
#                 self.sendRole("G", self.player_G)
#             threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

#     def command_listener(self):
#         threadingBool = True
#         while threadingBool:
#             cmd = input("Enter Command: ")
#             if cmd.lower() == "quit":
#                 print("Shutting down server...")
#                 threadingBool = False
#                 self.server.close()
#                 break
            
#             elif cmd.lower() == "1":
#                 self.activePlayer = self.player1

#     def send_confirmation(self, conf:bool, target:str, client):
#         data = {"purpose" : "confirmation",
#                 "target" : target,
#                 "confirmation" : conf}
#         client.send(json.dumps(data).encode())

#     def load_map(self, levelFile):
#         file_path = "Levels/"+levelFile+".json"
#         with open(file_path, 'r') as json_file:
#             data = json.load(json_file)

#         bluePrint = data["map"]

#         for entry in bluePrint:

#             if entry[1] == "tile":
#                 newTile = Tile(entry[2], entry[4], entry[0][0],entry[0][1],entry[3])
#                 self.map.append(newTile)

#             elif entry[1] == "door":
#                 newDoor = Door(entry[2], entry[4], entry[6], entry[0][0], entry[0][1], entry[3], entry[5])
#                 if entry[5] == False:
#                     newDoor.change_picture(newDoor.pictureClosedPath)
#                 self.map.append(newDoor)

#             elif entry[1] == "wall":
#                 newWall = Wall(entry[2],entry[0][0],entry[0][1])
#                 self.map.append(newWall)

#             elif entry[1] == "entry":
#                 newEntry = EntryPoint(entry[2],entry[0][0],entry[0][1],entry[3])
#                 self.map.append(newEntry)

#             elif entry[1] == "control":
#                 newControl = ControlledArea(entry[2],entry[4],entry[0][0],entry[0][1],entry[3])
#                 self.map.append(newControl)

#     def sendSetupData(self, levelFile, client):
#         file_path = "Levels/"+levelFile+".json"
#         data = {"purpose": "setup",
#                 "mapFile":file_path}
#         client.send(json.dumps(data).encode())

#     def sendRole(self, role, client):
#         data = {"purpose" : "role",
#                 "role" : role}
#         client.send(json.dumps(data).encode())

#     def start_server(self):
#         self.load_map("Level_1")
#         threading.Thread(target=self.accept_clients, daemon=True).start()

#     def sendMapUpdates(self, tiles):
#         data = {"purpose": "mapupdate",
#                 "tiles": tiles}
        
#         for client in self.clients:
#             client.send(json.dumps(data).encode())

#     def handle_lobby(self):
#         run = True

#         while run:
#             if self.gsready and self.smready:
#                 run = False
#                 self.run_game()

#     def run_game(self):
#         while True:
#             pass                                                                                      

# server = Test_Server()
# client = Client()
# server.start_server()
# client.start()