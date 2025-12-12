import socket
import threading
import json
from enum import Enum
from MultiplayerModels import *
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,  # Set to INFO, WARNING, or ERROR as needed
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("game.log"),  # Save logs to a file
        logging.StreamHandler()          # Also log to console
    ]
)

logger = logging.getLogger(__name__)

lock = threading.Lock()

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow keyboard interrupts to exit silently
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

# Override the default exception handler
sys.excepthook = handle_exception


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
        self.lock = threading.Lock()
        self.clients = []  # [(conn, addr, name, roll), ...]
        self.GSplayer = None
        self.SMplayer = None
        self.spectators  = []
        self.server_host = None
        self.running = True

        #Information for the setup
        self.isReadyToRecive = set()
        self.level = "1"
        self.available_blips = []
        self.reinforceing_blips = int
        self.isBroodLordPresent = False
        self.startBlips = int
        self.entrypoints = []

        #Information for the running game
        self.SMmodelList = []
        self.GSmodelList = []
        self.BLmodelList = []
        self.map = []
        self.activeModel = None
        self.recycle = bool
        self.to_place_blips = int
        self.bl_id = 0
        self.gs_id = 0

    def main(self):
        while True:     #this will perhaps be replaced by a variable to shut of the Server
            pass

    def start(self):
        """
        starts the server by binding it to its host and port and listening on that adress. After that it calls accept_clients
        and broadcast_listener as Threads.
        """
        if self.is_port_in_use(self.port, self.host):
            return False
        
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        threading.Thread(target=self.accept_clients, args=()).start()
        threading.Thread(target=self.broadcast_listener, daemon=True).start()
        logger.info(f"SERVER: Server started on Port {self.port} with Host {self.host}")
        return True

    def accept_clients(self):
        while self.running:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        name = None
        buffer = ""
        logger.info(f"SERVER: New connection: {addr}")
        try:
            while self.running:
                data = conn.recv(1024)
                if not data:
                    break
                
                buffer += data.decode()

                while "\n" in buffer:
                    raw_msg, buffer = buffer.split("\n", 1)

                    if not raw_msg.strip():
                        continue

                    try:
                        message = json.loads(raw_msg)
                    except json.JSONDecodeError as e:
                        logger.exception(f"SERVER: JSON decode error von {addr}: {e}, raw={raw_msg}")
                        continue

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
                        with lock:
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
                                    logger.info(f"SERVER: player {name}, {conn} has selected GS")
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
                                    logger.info(f"SERVER: player {name}, {conn} has selected SM")
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
                                logger.info(f"SERVER: player {name}, {conn} has selected Spectator")
                                self.send_lobby_update()

                    elif message["purpose"] == "start":
                        if self.SMplayer != None and self.GSplayer != None:
                            for c in self.clients:
                                self.send(c["conn"], {"purpose" : "start"})
                            threading.Thread(target=self.setup_lobby).start()

                    elif message["purpose"] == "readytorecive":
                        logger.info(f"SERVER: Ready recived from {addr}")
                        self.isReadyToRecive.add(addr)

                    elif message["purpose"] == "place":
                        with lock:
                            if self.SMplayer["conn"] == conn and self.SMplayer["addr"] == addr and self.SMplayer["name"] == name:
                                logger.info(f"MARINE PLACE REQUEST")
                                for tile in self.map:
                                    if tile.x == message["tile"][0] and tile.y == message["tile"][1]:
                                        logger.info(f"TILE FOUND AT {(tile.x, tile.y)}")
                                        if tile.is_occupied:
                                            break
                                        else:
                                            for model in self.SMmodelList:
                                                if model.ID == message["id"]:
                                                    logger.info(f"MODEL FOUND WITH ID:{model.ID}")
                                                    if model.position_x == None and model.position_y == None:
                                                        model.position_x = tile.x
                                                        model.position_y = tile.y
                                                        tile.is_occupied = True
                                                        tile.occupant = OccupantType.SPACEMARINE
                                                        self.send_game_update()
                                                        logger.info(f"SENDING UPDATE!")
                                                        break
                                                    else:
                                                        break
                    
                    elif message["purpose"] == "rotate_model":
                        logger.info(f"RECIVED TURN")
                        if self.SMplayer["conn"] == conn and self.SMplayer["addr"] == addr and self.SMplayer["name"] == name:
                            if message["phase"] == "deploy_sm":
                                for model in self.SMmodelList:
                                    if model.ID == message["id"]:
                                        if message["dir"] == "right":
                                            model.face = model.face.turn_right()
                                        elif message["dir"] == "left":
                                            model.face = model.face.turn_left()
                                        self.send_game_update()
                                        break

                    elif message["purpose"] == "finished_deploy":
                        if message["phase"] == "deploy_sm":
                            if self.SMplayer["conn"] == conn and self.SMplayer["addr"] == addr and self.SMplayer["name"] == name:
                                if self.startBlips != None:
                                    message_out = {"purpose": "wait"}
                                    self.send(self.SMplayer["conn"], message_out)
                                    self.to_place_blips = self.startBlips
                                    message_out["purpose"] = "place_bl"
                                    self.send(self.GSplayer["conn"], message)

                    elif message["purpose"] == "bl_request":
                        logger.info(f"REQUEST FOR BLIPS RECIVED")
                        if self.GSplayer["conn"] == conn and self.GSplayer["addr"] == addr and self.GSplayer["name"] == name:
                            if self.to_place_blips != 0:
                                bl_send = self.draw_blips()
                                message = {"purpose": "draw_blips", "blips": bl_send}
                                self.send(self.GSplayer["conn"], message)

                    if message["purpose"] == "disconnect":
                        with lock:
                            self.send(conn, {"Purpose": "disconnect"})
                            break

        except Exception as e:
            logger.exception(f"SERVER: Error with {addr}: {e}")
        finally:
            conn.close()
            if conn:
                with lock:
                    self.clients = [c for c in self.clients if c["conn"] != conn]
                    self.send_lobby_update()

                    if len(self.clients) == 0:
                        self.shutdown()

    def send(self, conn, message):
        conn.sendall((json.dumps(message) + "\n").encode())

    def send_lobby_update(self):
        players = [(c["name"], c["role"].name) for c in self.clients]
        for c in self.clients:
            self.send(c["conn"], {
                "purpose": "lobby_update",
                "players": players,
            })
    
    def send_game_update(self):
        send_map = []
        sm = []
        for tile in self.map:
            send_map.append(tile.send())

        for model in self.SMmodelList:
            sm.append(model.send())

        message = {
           "purpose": "game_update",
           "map": send_map,
           "sm": sm
            }
        
        for c in self.clients:
            self.send(c["conn"], message)

    def setup_lobby(self):
        logger.info(f"SERVER: Lobby started with {self.clients}")

        #loads the correct level data
        level_file = "Levels/" + "level_" + self.level + ".json"

        with open(level_file, 'r') as json_file:
            data = json.load(json_file)

        #sets the setup variables
        self.available_blips = data["blipList"]
        self.reinforceing_blips = data["reinforcement"]
        self.isBroodLordPresent = data["broodLord"]
        self.startBlips = data["startBlip"]
        self.entrypoints = data["entryPoints"]

        SMList = data["smModelList"]
        bluePrint = data["map"]

        #makes shure all clients are ready to recive the setup
        isReadyToSend = False

        for c in self.clients:
            self.send(c["conn"],{"purpose":"readyup"})

        while isReadyToSend == False:

            isReadyToSend = True

            for c in self.clients:
                if c["addr"] not in self.isReadyToRecive:
                    isReadyToSend  = False
                    self.send(c["conn"],{"purpose":"readyup"})

        #serialises the data for the clients
        for entry in SMList:
            marine = SpaceMarine(entry["id"], entry["weapon"], entry["rank"])
            self.SMmodelList.append(marine)
            logger.info(marine)

        for entry in bluePrint:
            match entry["type"]:
                case "tile":
                    tile = Tile.from_data(entry)
                case "door":
                    tile = Door.from_data(entry)
                case "wall":
                    tile = Wall.from_data(entry)
                case "entry":
                    tile = EntryPoint.from_data(entry)
            self.map.append(tile)

        sendMap = []
        for tile in self.map:
            sendMap.append(tile.send())
        sendRoster = []
        for model in self.SMmodelList:
            sendRoster.append(model.send())
        print (sendRoster[0])
        print("MAP:")
        print(sendMap)

        #sends data to the clients
        for c in self.clients:
            message = {"purpose":"setup","marines":sendRoster,"map":sendMap}
            self.send(c["conn"],message)
        
        print(self.SMmodelList)

        for c in self.clients:
            if c == self.SMplayer:
                self.send(c["conn"],{"purpose":"deploy_sm", "entries":self.entrypoints})
            else:
                self.send(c["conn"], {"purpose": "continue"})

    def broadcast_listener(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(("", self.discovery_port))

        while self.running:
            try:
                data, addr = udp_socket.recvfrom(1024)
                if data.decode() == "DISCOVER_SPACEHULK":
                    response = f"SPACEHULK_SERVER:{self.port}"
                    udp_socket.sendto(response.encode(), addr)
            except Exception as e:
                print("Discovery error:", e)

    def is_port_in_use(self, port, host):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False   # Port ist frei
            except OSError:
                return True    # Port ist belegt
            
    def draw_blips(self, amount):
        
        id_list = []

        for i in range(amount):
            if self.available_blips.__len__() == 0:
                break
            a = random.randint(0, self.available_blips.__len__()-1)
            blip = self.available_blips.pop(a)
            id = self.bl_id 
            self.bl_id +=1
            model = Blip(blip, id)
            self.BLmodelList.append(model)
            id_list.append(model.send())

        return(id_list)
    
    def shutdown(self):
        logger.info("SERVER: No clients left - shutting down server.")

        self.running = False

        try:
            self.server_socket.close()
        except:
            pass

        # Alle offenen Client-Sockets schließen
        for c in self.clients:
            try:
                c["conn"].close()
            except:
                pass

        self.clients.clear()


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