import socket
import threading
import json
import pygame
from Board import *
from Models import *

class Client:
    def __init__(self, host='127.0.0.1', port=5000):
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.map = []
        pygame.init()
        self.screen = pygame.display.set_mode((900, 900), pygame.DOUBLEBUF)
        self.running = True  # Flag to control the main loop
        self.role = None
        self.selectedTile = None
        self.clickedTile = None
        self.gameStates = {}
        self.SMmodelList

    def listen_to_server(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())

                match message["purpose"]:
                    case "setup":
                        print("setup")
                        self.load_map(message["mapFile"])
                    case "role":
                        self.role = message["role"]
                        print(self.role)
                    case "confirmation":
                        if message["target"] == "clicked":
                            if message["confirmation"] == True:
                                print("confirmed Clicked")
                            else:
                                self.clickedTile = None

            except Exception as e:
                print(f"Error in receiving: {e}")
                break

    def load_map(self, levelFile):
        file_path = levelFile
        try:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            print(f"Error: Level file '{file_path}' not found.")
            return

        bluePrint = data["map"]
        self.map.clear()  # Clear previous map data

        for entry in bluePrint:
            if entry[1] == "tile":
                newTile = Tile(entry[2], entry[4], entry[0][0], entry[0][1], entry[3])
                self.map.append(newTile)
            elif entry[1] == "door":
                newDoor = Door(entry[2], entry[4], entry[6], entry[0][0], entry[0][1], entry[3], entry[5])
                if not entry[5]:  # If door is closed
                    newDoor.change_picture(newDoor.pictureClosedPath)
                self.map.append(newDoor)
            elif entry[1] == "wall":
                newWall = Wall(entry[2], entry[0][0], entry[0][1])
                self.map.append(newWall)
            elif entry[1] == "entry":
                newEntry = EntryPoint(entry[2], entry[0][0], entry[0][1], entry[3])
                self.map.append(newEntry)
            elif entry[1] == "control":
                newControl = ControlledArea(entry[2], entry[4], entry[0][0], entry[0][1], entry[3])
                self.map.append(newControl)

        for tile in self.map:
            tile.render(self.screen)  # Render the tiles
        pygame.display.flip()  # Update the display

    def send_message(self, purpose:str):
        data = {"purpose": purpose}
        self.client_socket.send(json.dumps(data).encode())

    def send_message_clicked(self, tile):
        data = {"purpose": "clicked",
                "tile" : (tile.x, tile.y)}
        self.client_socket.send(json.dumps(data).encode())

    def start(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            threading.Thread(target=self.listen_to_server, daemon=True).start()

            # Main Pygame Loop
            while self.running:
                self.screen.fill((0, 0, 0))  # Clear the screen

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False  # Stop the loop when window is closed
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        for tile in self.map:
                            if isinstance(tile, Tile):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    self.clickedTile = tile
                                    self.send_message_clicked(tile)
                                    

                pygame.time.delay(30)  # Control frame rate

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()
            pygame.quit()
            print("Disconnected from server.")

class ClientSpacemarinePlaceGamestate:

    def __init__(self, client):
        self.client = client

client = Client()
client.start()