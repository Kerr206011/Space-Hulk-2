import socket
import threading
import json
import pygame
from Board import *
from Models import *
from UI import * 
from MultiplayerClassServer import Server

class Test_Client:
    def __init__(self, host='127.0.0.1', port=5000, name='Player1'):
        try:
            with open("config.json", 'r') as json_file:
                data = json.load(json_file)
                self.name = data["name"]
        except:
            self.name = name
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players_in_lobby = []
        self.is_host = False
        pygame.init()
        pygame.display.set_caption("Space Hulk")
        self.screen = pygame.display.set_mode((900,700))
        self.state = None

    def main(self):
        picture = pygame.image.load("Pictures/Buttons/Accept.png")
        startButton = Button(400, 300, picture, 1)
        hostButton = Button(400, 400, picture, 1)
        configButton = Button(40, 600, picture, 1)
        self.screen.fill('black')
        startButton.draw(self.screen)
        hostButton.draw(self.screen)
        configButton.draw(self.screen)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if startButton.rect.collidepoint(pygame.mouse.get_pos()):
                        self.connect()
                    elif hostButton.rect.collidepoint(pygame.mouse.get_pos()):
                        self.gameStat_lobby()
                        self.connect()
                    elif configButton.rect.collidepoint(pygame.mouse.get_pos()):
                        self.config()

    def config(self):
        self.screen.fill('black')
        picture = pygame.image.load("Pictures/Buttons/Accept.png")
        acceptButton = Button(400, 600, picture, 1)
        font = pygame.font.SysFont(None, 32)
        file_path = "config.json"
        name:str = self.name
        acceptButton.draw(self.screen)
        self.screen.blit(font.render(name, True, 'green'),(200,200))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                #events werden ohne auftretendes event aufgerufen
                elif (event.type == pygame.MOUSEBUTTONUP and acceptButton.rect.collidepoint(pygame.mouse.get_pos())) or (event.key == pygame.K_KP_ENTER) or (event.key == pygame.K_RETURN):
                    if name.__len__() != 0:
                        self.name = name
                        data = {"name": self.name}
                        with open(file_path, 'w') as json_file:
                            json.dump(data, json_file, indent=4)
                       # return
                        self.main()
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
                    self.screen.fill('black')
                    self.screen.blit(font.render(name, True, 'green'),(200,200))
                    acceptButton.draw(self.screen)
                    pygame.display.flip()


    def connect(self):
        self.client_socket.connect((self.server_host, self.server_port))
        # Namen an Server schicken
        self.send({
            "purpose": "join_lobby",
            "name": self.name
        })
        self.running = True
        threading.Thread(target=self.listen_to_server).start()

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
                        self.players_in_lobby = message["players"]
                        print("Lobby joined:", self.players_in_lobby)
                    case "lobby_update":
                        self.players_in_lobby = message["players"]
                        print("Lobby update:", self.players_in_lobby)
                    case "start_game":
                        print("Spiel startet!")

            except Exception as e:
                print("Fehler in Lobby:", e)
                break
            
    def gameStat_lobby(self):
        test_server = Server()
        threading.Thread(target=test_server.start, args=(), daemon = True).start()
        self.is_host = True

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