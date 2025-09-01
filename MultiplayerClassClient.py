import socket
import threading
import json
import pygame
from UI import * 
from MultiplayerClassServer import *

class Game_State(Enum):
    MAINMENU = "main"
    LOBBY = "lobby"
    CONFIG = "config"
    SETUP = "setup"

class Test_Client:
    def __init__(self, host='127.0.0.1', port=5000, name='Player1'):
        try:
            with open("config.json", 'r') as json_file:
                data = json.load(json_file)
                self.name = data["name"]
        except:
            self.name = name

        self.role = GameRole.SPECTATOR
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players_in_lobby = []
        self.is_host = False
        pygame.init()
        pygame.display.set_caption("Space Hulk")
        self.screen = pygame.display.set_mode((900,700))
        self.state = None
        self.running = False

        #global level variables
        self.level = None

    def main(self):
        #general init
        stateShift = False
        wait  =False

        #main menu init
        main_picture = pygame.image.load("Pictures/Buttons/Accept.png")
        main_startButton = Button(400, 300, main_picture, 1)
        main_hostButton = Button(400, 400, main_picture, 1)
        main_configButton = Button(40, 600, main_picture, 1)

        #config init
        config_picture = pygame.image.load("Pictures/Buttons/Accept.png")
        config_acceptButton = Button(400, 600, config_picture, 1)
        config_font = pygame.font.SysFont(None, 32)
        config_file_path = "config.json"
        config_name:str = self.name

        #lobby init
        lobby_name_pos_spectator = 100
        lobby_name_pos_gs = 100
        lobby_name_pos_sm = 100
        lobby_picture = pygame.image.load("Pictures/Buttons/Accept.png")
        lobby_GSButton = Button(200, 600, config_picture, 1)
        lobby_spectatorButton = Button(400, 600, config_picture, 1)
        lobby_SMButton = Button(600, 600, config_picture, 1)
        lobby_startButton = Button(100, 600, config_picture, 1)

        #setup init
        setup_levelName = None
        setup_isReady = False

        #start of game
        self.screen.fill('black')
        main_startButton.draw(self.screen)
        main_hostButton.draw(self.screen)
        main_configButton.draw(self.screen)
        pygame.display.flip()
        self.state = Game_State.MAINMENU

        while True:
            wait = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                #main menu logic
                elif self.state == Game_State.MAINMENU and not wait:
                    if event.type == pygame.MOUSEBUTTONUP:
                        if main_startButton.rect.collidepoint(pygame.mouse.get_pos()):
                            self.screen.fill('black')
                            self.screen.blit(config_font.render("connecting", True, 'green'),(300,400))
                            pygame.display.flip()
                            self.connect()
                            self.state = Game_State.LOBBY
                            stateShift = True
                            wait = True

                        elif main_hostButton.rect.collidepoint(pygame.mouse.get_pos()):
                            self.gameStat_lobby()
                            self.screen.fill('black')
                            self.screen.blit(config_font.render("connecting", True, 'green'),(300,400))
                            pygame.display.flip()
                            self.connect()
                            self.state = Game_State.LOBBY
                            stateShift = True
                            wait = True

                        elif main_configButton.rect.collidepoint(pygame.mouse.get_pos()):
                            stateShift = True
                            self.state = Game_State.CONFIG
                            wait = True

                #config logic
                elif self.state == Game_State.CONFIG and not wait:
                    if event.type == pygame.MOUSEBUTTONUP and config_acceptButton.rect.collidepoint(pygame.mouse.get_pos()):
                        if config_name.__len__() != 0:
                            self.name = config_name
                            data = {"name": self.name}
                            with open(config_file_path, 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                            stateShift = True
                            self.state = Game_State.MAINMENU
                            wait = True
                        
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            config_name = config_name[:-1]

                        elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                            if config_name.__len__() != 0:
                                self.name = config_name
                                data = {"name": self.name}
                                with open(config_file_path, 'w') as json_file:
                                    json.dump(data, json_file, indent=4)
                                stateShift = True
                                self.state = Game_State.MAINMENU
                                wait = True

                        else:
                            config_name += event.unicode
                        self.screen.fill('black')
                        self.screen.blit(config_font.render(config_name, True, 'green'),(200,200))
                        config_acceptButton.draw(self.screen)
                        pygame.display.flip()

                #lobby logic
                elif self.state == Game_State.LOBBY:
                    if event.type == pygame.USEREVENT:
                        if event.data["purpose"] == "lobby_update":
                            self.screen.fill('black')
                            lobby_GSButton.draw(self.screen)
                            lobby_SMButton.draw(self.screen)
                            lobby_spectatorButton.draw(self.screen)
                            if self.is_host:
                                lobby_startButton.draw(self.screen)

                            lobby_name_pos_spectator = 100

                            for player in self.players_in_lobby:
                                if player[1] == GameRole.SPECTATOR:
                                    self.screen.blit(config_font.render(player[0], True, 'green',), (300, lobby_name_pos_spectator))
                                    lobby_name_pos_spectator += 50
                                elif player[1] == GameRole.SPACEMARINE:
                                    self.screen.blit(config_font.render(player[0], True, 'blue',), (500, lobby_name_pos_sm))
                                else:
                                    self.screen.blit(config_font.render(player[0], True, 'purple',), (100, lobby_name_pos_gs))

                            pygame.display.flip()

                        elif event.data["purpose"] == "start":
                            stateShift = True
                            self.state = Game_State.SETUP
                            wait = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.disconnect()
                            self.state = Game_State.MAINMENU
                            stateShift = True
                            wait = True
                        
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if lobby_GSButton.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.role != GameRole.GENSTEALER:
                                request = True
                                for player in self.players_in_lobby:
                                    if player[1] == GameRole.GENSTEALER:
                                        request = False
                                if request == True:
                                    message = {"purpose":"rolechange",
                                               "role" : "genstealer"}
                                    self.send(message)

                        elif lobby_SMButton.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.role != GameRole.SPACEMARINE:
                                request = True
                                for player in self.players_in_lobby:
                                    if player[1] == GameRole.SPACEMARINE:
                                        request = False
                                if request == True:
                                    message = {"purpose":"rolechange",
                                               "role" : "spacemarine"}
                                    self.send(message)

                        elif lobby_spectatorButton.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.role != GameRole.SPECTATOR:
                                message = {"purpose":"rolechange",
                                            "role" : "spectator"}
                                self.send(message)
                        
                        elif self.is_host:
                            if lobby_startButton.rect.collidepoint(pygame.mouse.get_pos()):
                                message = {"purpose" : "start"}
                                self.send(message)

                elif self.state == Game_State.SETUP and not wait:
                    if setup_isReady == False:
                        self.send({"purpose" : "readytorecive"})
                    
                    if event.type == pygame.USEREVENT:
                        if event.data ["purpose"] == "setup":
                            if self.role == GameRole.SPACEMARINE:
                                setup_levelName = data["level"]

            #updates the screen after a stateshift
            if stateShift == True:
                if self.state == Game_State.MAINMENU:  
                    self.screen.fill('black')
                    main_startButton.draw(self.screen)
                    main_hostButton.draw(self.screen)
                    main_configButton.draw(self.screen)

                if self.state == Game_State.CONFIG:
                    self.screen.fill('black')
                    config_acceptButton.draw(self.screen)
                    self.screen.blit(config_font.render(config_name, True, 'green'),(200,200))
                
                if self.state == Game_State.LOBBY:
                    self.screen.fill('black')
                    self.screen.blit(config_font.render("Connecting", True, 'green',), (300, 400))
                    lobby_GSButton.draw(self.screen)
                    lobby_SMButton.draw(self.screen)
                    lobby_spectatorButton.draw(self.screen)
                    if self.is_host:
                        lobby_startButton.draw(self.screen)

                if self.state == Game_State.SETUP:
                    self.screen.fill('black')
                    self.screen.blit(config_font.render("Loading Level: 0%", True, 'green',), (300, 400))
                    
    
                pygame.display.flip()
                stateShift = False

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # NEU anlegen
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            self.send({ "purpose": "join_lobby", "name": self.name })
            self.running = True
            threading.Thread(target=self.listen_to_server).start()
        except:
            lobbys = self.discover_servers()
            self.client_socket.connect((lobbys[0][0], lobbys[0][1]))
            self.send({ "purpose": "join_lobby", "name": self.name })
            self.running = True
            threading.Thread(target=self.listen_to_server).start()


    def disconnect(self):
        try:
            # Server informieren (optional)
            self.send({"purpose": "disconnect"})
        except:
            pass
        finally:
            self.running = False   # stoppe Empfangs-Thread
            self.client_socket.close()
            print("Verbindung getrennt")

    def send(self, message):
        self.client_socket.sendall(json.dumps(message).encode())

    def listen_to_server(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())

                match message["purpose"]:
                    case "lobby_joined":
                        self.players_in_lobby = []
                        for player in message["players"]:
                            self.players_in_lobby.append([player[0], GameRole[player[1]]])
                        print("Lobby joined:", self.players_in_lobby)
                    case "lobby_update":
                        self.players_in_lobby = []
                        for player in message["players"]:
                            self.players_in_lobby.append([player[0], GameRole[player[1]]])
                        print("Lobby joined:", self.players_in_lobby)
                    case "rolechange":
                        self.role = GameRole[message["role"]]
                    case "start_game":
                        print("Spiel startet!")

                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"data" : message}))

            except Exception as e:
                print("Fehler in Lobby:", e)
                break
            
    def gameStat_lobby(self):
        test_server = Server()
        threading.Thread(target=test_server.start, args=(), daemon = True).start()
        self.is_host = True
    
    def discover_servers(self, discovery_port=5001, timeout=1):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.settimeout(timeout)

        message = "DISCOVER_SPACEHULK".encode()
        udp_socket.sendto(message, ("<broadcast>", discovery_port))

        servers = []
        try:
            while True:
                data, addr = udp_socket.recvfrom(1024)
                if data.decode().startswith("SPACEHULK_SERVER:"):
                    port = int(data.decode().split(":")[1])
                    servers.append((addr[0], port))
        except socket.timeout:
            pass

        return servers

client = Test_Client()
client.main()

# class Test_Client:
#     def __init__(self, host='127.0.0.1', port=5000):
#         self.server_host = host
#         self.server_port = port
#         self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.map = []
#         pygame.init()
#         self.screen = pygame.display.set_mode((900, 900), pygame.DOUBLEBUF)
#         self.running = True  # Flag to control the main loop
#         self.role = None
#         self.selectedTile = None
#         self.clickedTile = None

#         self.lobbyMemberList = []
#         self.Spectators = []

#         self.gameStates = {}
#         self.SMModelList = []
#         self.GSModelList = []
#         self.BLModelList = []

#     def listen_to_server(self):
#         while self.running:
#             try:
#                 data = self.client_socket.recv(1024)
#                 if not data:
#                     break
#                 message = json.loads(data.decode())

#                 match message["purpose"]:
#                     case "setup":
#                         print("setup")
#                         self.load_map(message["mapFile"])
#                     case "role":
#                         self.role = message["role"]
#                         print(self.role)
#                     case "confirmation":
#                         if message["target"] == "clicked":
#                             if message["confirmation"] == True:
#                                 print("confirmed Clicked")
#                             else:
#                                 self.clickedTile = None

#             except Exception as e:
#                 print(f"Error in receiving: {e}")
#                 break

#     def load_map(self, levelFile):
#         file_path = levelFile
#         try:
#             with open(file_path, 'r') as json_file:
#                 data = json.load(json_file)
#         except FileNotFoundError:
#             print(f"Error: Level file '{file_path}' not found.")
#             return

#         bluePrint = data["map"]
#         self.map.clear()  # Clear previous map data

#         for entry in bluePrint:
#             if entry[1] == "tile":
#                 newTile = Tile(entry[2], entry[4], entry[0][0], entry[0][1], entry[3])
#                 self.map.append(newTile)
#             elif entry[1] == "door":
#                 newDoor = Door(entry[2], entry[4], entry[6], entry[0][0], entry[0][1], entry[3], entry[5])
#                 if not entry[5]:  # If door is closed
#                     newDoor.change_picture(newDoor.pictureClosedPath)
#                 self.map.append(newDoor)
#             elif entry[1] == "wall":
#                 newWall = Wall(entry[2], entry[0][0], entry[0][1])
#                 self.map.append(newWall)
#             elif entry[1] == "entry":
#                 newEntry = EntryPoint(entry[2], entry[0][0], entry[0][1], entry[3])
#                 self.map.append(newEntry)
#             elif entry[1] == "control":
#                 newControl = ControlledArea(entry[2], entry[4], entry[0][0], entry[0][1], entry[3])
#                 self.map.append(newControl)

#         for tile in self.map:
#             tile.render(self.screen)  # Render the tiles
#         pygame.display.flip()  # Update the display

#     def send_message(self, purpose:str):
#         data = {"purpose": purpose}
#         self.client_socket.send(json.dumps(data).encode())

#     def send_message_clicked(self, tile):
#         data = {"purpose": "clicked",
#                 "tile" : (tile.x, tile.y)}
#         self.client_socket.send(json.dumps(data).encode())

#     def start(self):
#         try:
#             self.client_socket.connect((self.server_host, self.server_port))
#             threading.Thread(target=self.listen_to_server, daemon=True).start()

#             # Main Pygame Loop
#             while self.running:
#                 self.screen.fill((0, 0, 0))  # Clear the screen

#                 for event in pygame.event.get():
#                     if event.type == pygame.QUIT:
#                         self.running = False  # Stop the loop when window is closed
                    
#                     elif event.type == pygame.MOUSEBUTTONDOWN:
#                         for tile in self.map:
#                             if isinstance(tile, Tile):
#                                 if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
#                                     self.clickedTile = tile
#                                     self.send_message_clicked(tile)
                                    

#                 pygame.time.delay(30)  # Control frame rate

#         except Exception as e:
#             print(f"Error: {e}")
#         finally:
#             self.client_socket.close()
#             pygame.quit()
#             print("Disconnected from server.")

#     def run(self):
#         pass

#     def run_lobby(self):
#         while self.running:

#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.running = False  # Stop the loop when window is closed
#                     pygame.quit()
#                     sys.exit()

#             for player in self.lobbyMemberList:
#                 if player == self.SMPlayer:
#                     pygame.draw.rect(self.screen, "blue", pygame.Rect(10,10,20,10))
#                 else:
#                     pygame.draw.rect(self.screen, "red", pygame.Rect(200,10,20,10))
#             pygame.display.flip()


# class Client:

#     def __init__(self, host, port):
#         self.server_host = host
#         self.server_port = port
#         self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.map = []
#         pygame.init()
#         self.screen = pygame.display.set_mode((900, 900), pygame.DOUBLEBUF)
#         self.running = True  # Flag to control the main loop

#         self.role = None
#         self.selectedTile = None
#         self.clickedTile = None
#         self.selectedModel = None
#         self.clickedModel = None 

#         self.lobbyMemberList = []

#         self.SMModelList = []
#         self.GSModelList = []
#         self.BLModelList = []

#     def listen_to_server(self):
#         while self.running:
#             try:
#                 data = self.client_socket.recv(1024)
#                 if not data:
#                     break
#                 message = json.loads(data.decode())

#                 match message["purpose"]:
#                     case "setup":
#                         print("setup")
#                         self.load_map(message["mapFile"])
#                     case "role":
#                         self.role = message["role"]
#                         print(self.role)
#                     case "confirmation":
#                         if message["target"] == "clicked":
#                             if message["confirmation"] == True:
#                                 print("confirmed Clicked")
#                             else:
#                                 self.clickedTile = None

#             except Exception as e:
#                 print(f"Error in receiving: {e}")
#                 break

#     def load_map(self, levelFile):
#         file_path = levelFile
#         try:
#             with open(file_path, 'r') as json_file:
#                 data = json.load(json_file)
#         except FileNotFoundError:
#             print(f"Error: Level file '{file_path}' not found.")
#             return

#         bluePrint = data["map"]
#         self.map.clear()  # Clear previous map data

#         for entry in bluePrint:
#             if entry[1] == "tile":
#                 newTile = Tile(entry[2], entry[4], entry[0][0], entry[0][1], entry[3])
#                 self.map.append(newTile)
#             elif entry[1] == "door":
#                 newDoor = Door(entry[2], entry[4], entry[6], entry[0][0], entry[0][1], entry[3], entry[5])
#                 if not entry[5]:  # If door is closed
#                     newDoor.change_picture(newDoor.pictureClosedPath)
#                 self.map.append(newDoor)
#             elif entry[1] == "wall":
#                 newWall = Wall(entry[2], entry[0][0], entry[0][1])
#                 self.map.append(newWall)
#             elif entry[1] == "entry":
#                 newEntry = EntryPoint(entry[2], entry[0][0], entry[0][1], entry[3])
#                 self.map.append(newEntry)
#             elif entry[1] == "control":
#                 newControl = ControlledArea(entry[2], entry[4], entry[0][0], entry[0][1], entry[3])
#                 self.map.append(newControl)

#         for tile in self.map:
#             tile.render(self.screen)  # Render the tiles
#         pygame.display.flip()  # Update the display

#     def send_message(self, purpose:str):
#         data = {"purpose": purpose}
#         self.client_socket.send(json.dumps(data).encode())

#     def send_message_clicked(self, tile):
#         data = {"purpose": "clicked",
#                 "tile" : (tile.x, tile.y)}
#         self.client_socket.send(json.dumps(data).encode())

#     def send_message_roleChanged(self, role):
#         data = {"purpose": "roleswitch",
#                 "new_role": role}

#     def start(self):
#         try:
#             self.client_socket.connect((self.server_host, self.server_port))
#             threading.Thread(target=self.listen_to_server, daemon=True).start()

#             # Main Pygame Loop
#             while self.running:
#                 self.screen.fill((0, 0, 0))  # Clear the screen

#                 for event in pygame.event.get():
#                     if event.type == pygame.QUIT:
#                         self.running = False  # Stop the loop when window is closed
                    
#                     elif event.type == pygame.MOUSEBUTTONDOWN:
#                         for tile in self.map:
#                             if isinstance(tile, Tile):
#                                 if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
#                                     self.clickedTile = tile
#                                     self.send_message_clicked(tile)
                                    

#                 pygame.time.delay(30)  # Control frame rate

#         except Exception as e:
#             print(f"Error: {e}")
#         finally:
#             self.client_socket.close()
#             pygame.quit()
#             print("Disconnected from server.")

#     def run(self):
#         pass

#     def run_lobby(self):
#         lobbySlots = {
#             "SM":{
#                 (1,(100, 10)),
#                 (2,(100, 20))
#         },
#             "GS":{
#                 (1, (500, 10)),
#                 (2,(500, 20))
#             },
#             "Spectator":{
#                 (1, (250, 800)),
#                 (2, (350, 800))
#             }                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
#         }

#         SM_Picture = pygame.image.load('Pictures/Tiles/Floor_1.png')
#         SM_Button = Button(10, 800, SM_Picture, 1)
#         GS_Picture = pygame.image.load('Pictures/Tiles/Floor_1.png')
#         GS_Button = Button(500, 800, GS_Picture, 1)

#         while self.running:

#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.running = False  # Stop the loop when window is closed
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     if SM_Button.rect.collidepoint(pygame.mouse.get_pos()):
#                         self.role = "SM"
                    
#                     elif GS_Button.rect.collidepoint(pygame.mouse.get_pos()):
#                         self.role = "GS"
                        
#             pygame.display.flip()


# client = Client()
# client.start()