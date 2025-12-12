import socket
import threading
import json
import pygame
from UI import * 
from MultiplayerClassServer import *

class SpaceMarineSprite:
    def __init__(self, pos_x, pos_y, scale, picture_path: str, face, ID):
        self.face = Facing((face[0], face[1]))
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.graphic_x = pos_x
        self.graphic_y = pos_y
        self.picture_path = picture_path    #perhaps unnececary but left in for possible future use
        image = pygame.image.load(picture_path).convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()
        self.id = ID
        
        match self.face:
            case Facing.NORTH:
                self.image = pygame.transform.rotate(self.image, 90)
            
            case Facing.EAST:
                pass

            case Facing.SOUTH:
                self.image = pygame.transform.rotate(self.image, 180)

            case Facing.WEST:
                self.image = pygame.transform.rotate(self.image, -90)
 
    @classmethod
    def from_data(cls, data, scale):
        return SpaceMarineSprite(data["pos_x"], data["pos_y"], scale, data["picture"], data["face"], data["id"])

    def draw(self, screen):
        self.rect.topleft = (self.graphic_x * self.image.get_width(), self.graphic_y * self.image.get_height())
        screen.blit(self.image, self.rect)

    def align(self, sprite):
        self.graphic_x = sprite.graphic_x
        self.graphic_y = sprite.graphic_y

        self.pos_x = sprite.x
        self.pos_y = sprite.y
            
    def move(self, direction):
        self.graphic_x += direction[0]
        self.graphic_y += direction[1]

    def rescale(self, scale):
        image = self.image
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()

    def turn(self, dir):

        print(self.face, dir)
        counter = 0
        while (self.face.value[0] != dir[0] or self.face.value[1] != dir[1]):
            if counter == 100:
                print("counter error")
                break
            
            counter +=1

            self.face = self.face.turn_right()

            print(self.face.value[0], self.face.value[1], dir)

            self.image = pygame.transform.rotate(self.image, -90)

    def to_dict(self):
        return{
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "id": self.id
        }

    def __repr__(self):
        return (f"<SpaceMarine pos=({self.pos_x},{self.pos_y}), face:{self.face}, ID:{self.id}>")

class BlipSprite:
    def __init__(self, pos_x, pos_y, scale, picture_path: str, ID):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.graphic_x = pos_x
        self.graphic_y = pos_y
        self.picture_path = picture_path
        image = pygame.image.load(picture_path).convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()
        self.id = ID

    @classmethod
    def from_data(cls, data, scale):
        return BlipSprite(data["pos_x"], data["pos_y"], scale, data["picture"], data["id"])

    def draw(self, screen):
        self.rect.topleft = (self.graphic_x * self.image.get_width(), self.graphic_y * self.image.get_height())
        screen.blit(self.image, self.rect)

    def align(self, sprite):
        self.graphic_x = sprite.graphic_x
        self.graphic_y = sprite.graphic_y

        self.pos_x = sprite.x
        self.pos_y = sprite.y

    def move(self, direction):
        self.graphic_x += direction[0]
        self.graphic_y += direction[1]

    def rescale(self, scale):
        image = self.image
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()

    def __repr__(self):
        return (f"<Blip pos=({self.pos_x},{self.pos_y})>")

class GenstealerSprite:
    def __init__(self, pos_x, pos_y, scale, picture_path: str, face, broodlord):
        self.broodlord = broodlord
        self.face = Facing((face[0], face[1]))
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.graphic_x = pos_x
        self.graphic_y = pos_y
        self.picture_path = picture_path
        image = pygame.image.load(picture_path).convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()

        match self.face:
            case Facing.NORTH:
                self.image = pygame.transform.rotate(self.image, 90)
            
            case Facing.EAST:
                pass

            case Facing.SOUTH:
                self.image = pygame.transform.rotate(self.image, 180)

            case Facing.WEST:
                self.image = pygame.transform.rotate(self.image, -90)

    @classmethod
    def from_data(cls, data, scale):
        return GenstealerSprite(data["pos_x"], data["pos_y"], scale, data["picture"], data["face"], data["broodlord"])

    def draw(self, screen):
        self.rect.topleft = (self.graphic_x * self.image.get_width(), self.graphic_y * self.image.get_height())
        screen.blit(self.image, self.rect)

    def align(self, sprite):
        self.graphic_x = sprite.graphic_x
        self.graphic_y = sprite.graphic_y

        self.pos_x = sprite.x
        self.pos_y = sprite.y

    def move(self, direction):
        self.graphic_x += direction[0]
        self.graphic_y += direction[1]

    def rescale(self, scale):
        image = self.image
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()

    def turn(self, degr):
        self.image = pygame.transform.rotate(self.image, degr)

    def __repr__(self):
        return (f"<Genstealer pos=({self.pos_x},{self.pos_y}), face:{self.face}, Broodlord:{self.broodlord}>")

class TileSprite:
    def __init__(self, x, y, scale, picture_path, is_burning = False, has_item = False):
        self.x = x
        self.y = y
        self.graphic_x = x
        self.graphic_y = y
        self.is_burning = is_burning
        self.has_item = has_item    #perhaps not needed, but here for possible furure use
        self.scale = scale
        self.picture_path = picture_path+".png"
        self.burning_picture_path = picture_path+"_burning.png"
        image = pygame.image.load(self.picture_path).convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()

    @classmethod
    def from_data(cls, data, scale):
        return TileSprite(data["pos_x"], data["pos_y"], scale, data["picture"], data["is_burning"], data["has_item"])
    
    def draw(self, screen):
        self.rect.topleft = (self.graphic_x * self.image.get_width(), self.graphic_y * self.image.get_height())
        screen.blit(self.image, self.rect)

    def __repr__(self):
        return (f"<Tile pos=({self.x},{self.y}), burning={self.is_burning}>")
    
    def rescale(self, scale):
        image = self.image
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()

    def move(self, direction):
        self.graphic_x += direction[0]
        self.graphic_y += direction[1]

    def ignite(self, scale):
        image = pygame.image.load(self.burning_picture_path).convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()


class DoorSprite(TileSprite):
    def __init__(self, x, y, scale, picture_path, is_burning=False, has_item=False, is_open = False):
        super().__init__(x, y, scale, picture_path, is_burning, has_item)
        self.picture_path_open = picture_path+"_open.png"
        self.is_open = is_open

    @classmethod
    def from_data(cls, data, scale):
        return DoorSprite(data["pos_x"], data["pos_y"], scale, data["picture"], data["is_burning"], data["has_item"], data["is_open"])

    def interact(self, scale):
        if self.is_open:
            image = pygame.image.load(self.picture_path).convert_alpha()
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            self.image = pygame.transform.scale(image, (width, height))
            self.rect = self.image.get_rect()
            self.is_open = False
        else:
            image = pygame.image.load(self.picture_path_open).convert_alpha()
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            self.image = pygame.transform.scale(image, (width, height))
            self.rect = self.image.get_rect()
    
    def draw(self, screen):
        self.rect.topleft = (self.graphic_x * self.image.get_width(), self.graphic_y * self.image.get_height())
        screen.blit(self.image, self.rect)

    def move(self, direction):
        self.graphic_x += direction[0]
        self.graphic_y += direction[1]

class WallSprite:
    def __init__(self, x, y,scale, picture_path):
        self.x = x
        self.y = y
        self.graphic_x = x
        self.graphic_y = y
        self.scale = scale
        self.picture_path = picture_path+".png"
        image = pygame.image.load(self.picture_path).convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()

    def __repr__(self):
        return (f"<Tile pos=({self.x},{self.y})>")

    @classmethod
    def from_data(cls, data, scale):
        return WallSprite(data["pos_x"], data["pos_y"], scale, data["picture"])
    
    def rescale(self, scale):
        image = self.image
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()
    
    def draw(self, screen):
        self.rect.topleft = (self.graphic_x * self.image.get_width(), self.graphic_y * self.image.get_height())
        screen.blit(self.image, self.rect)

    def move(self, direction):
        self.graphic_x += direction[0]
        self.graphic_y += direction[1]

class EntryPointSprite:
    def __init__(self, x, y,scale, picture_path, blips, face):
        self.x = x
        self.y = y
        self.graphic_x = x
        self.graphic_y = y
        self.scale = scale
        self.picture_path = picture_path+".png"
        self.blips = blips
        self.face = face
        image = pygame.image.load(self.picture_path).convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()

    def __repr__(self):
        return (f"<Tile pos=({self.x},{self.y})>")

    @classmethod
    def from_data(cls, data, scale):
        return EntryPointSprite(data["pos_x"], data["pos_y"], scale, data["picture"], data["blips"], data["face"])
    
    def rescale(self, scale):
        image = self.image
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()
    
    def draw(self, screen):
        self.rect.topleft = (self.graphic_x * self.image.get_width(), self.graphic_y * self.image.get_height())
        screen.blit(self.image, self.rect)

    def move(self, direction):
        self.graphic_x += direction[0]
        self.graphic_y += direction[1]



class Game_State(Enum):
    MAINMENU = "main"
    LOBBY = "lobby"
    CONFIG = "config"
    SETUP = "setup"
    DEPLOY_SM = "deploy_sm"
    DEPLOY_BL = "deploy_bl"
    READY = "ready" #placeholder to check if setup is correct

class Test_Client:
    def __init__(self, host='127.0.0.1', port=5000, name='Player1', scale = 1):
        try:
            with open("config.json", 'r') as json_file:
                data = json.load(json_file)
                self.name = data["name"]
                self.scale = data["scale"]
        except:
            self.name = name
            self.scale = scale

        self.role = GameRole.SPECTATOR
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players_in_lobby = []
        self.is_host = False
        self.state = None
        self.running = False

        #global graphic variables
        pygame.init()
        pygame.display.set_caption("Space Hulk")
        self.screen = pygame.display.set_mode((900,700))
        self.button_bar = pygame.Rect(0, 600, 900, 100)

        #global level variables
        self.level = None
        self.smlist = []
        self.map = []
        self.bllist = []
        self.selected_tile = None
        

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
        config_slider = Slider(500, 500)
        config_active_slider = None
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

        #deploy_sm init
        deploysm_top_sprites_start = 5
        deploysm_selected_sprite = None
        deploysm_to_place_sprites = []
        deploysm_marked_tiles = []

        deploysm_deployButton = Button(200, 600, config_picture, 1)
        deploysm_rotateButton_left = Button(300, 600, config_picture, 1)
        deploysm_rotateButton_right = Button(400, 600, config_picture, 1)
        deploysm_finishButton = Button(500, 600, config_picture, 1)

        #deploy_gs init
        deploybl_top_sprites_start = 5
        deploybl_selected_sprite = None
        deploybl_to_place_sprites = []
        deploybl_marked_tiles = []
        deploybl_requested = False

        deploybl_deployButton = Button(200, 600, config_picture, 1)
        deploybl_rotateButton_left = Button(300, 600, config_picture, 1)
        deploybl_rotateButton_right = Button(400, 600, config_picture, 1)
        deploybl_finishButton = Button(700, 600, config_picture, 1)


        #gameplay init
        await_server_answer = False

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
                            if self.connect() == False:
                                stateShift = True
                                wait = True
                            else:
                                self.state = Game_State.LOBBY
                                stateShift = True
                                wait = True

                        elif main_hostButton.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.gameStat_lobby():
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
                    if event.type == pygame.MOUSEBUTTONUP: 
                        config_active_slider = None
                        if config_acceptButton.rect.collidepoint(pygame.mouse.get_pos()):
                            if config_name.__len__() != 0:
                                self.name = config_name
                                self.scale = config_slider.value()
                                data = {"name": self.name,
                                        "scale": self.scale}
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
                        config_slider.draw(self.screen)
                        pygame.display.flip()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if config_slider.rect.collidepoint(pygame.mouse.get_pos()):
                            config_active_slider = config_slider
                            self.screen.fill('black')
                            self.screen.blit(config_font.render(config_name, True, 'green'),(200,200))
                            config_acceptButton.draw(self.screen)
                            config_active_slider.slide()
                            config_active_slider.draw(self.screen)
                            pygame.display.flip()

                    elif event.type == pygame.MOUSEMOTION:
                        if config_active_slider != None:
                            self.screen.fill('black')
                            self.screen.blit(config_font.render(config_name, True, 'green'),(200,200))
                            config_acceptButton.draw(self.screen)
                            config_active_slider.slide()
                            config_active_slider.draw(self.screen)
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
                                print("start send")

                #setup logic
                elif self.state == Game_State.SETUP and not wait:
                    if event.type == pygame.USEREVENT:
                        if event.data["purpose"] == "setup":
                            # print(event.data)
                            for entry in event.data["marines"]:
                                self.smlist.append(SpaceMarineSprite.from_data(entry, self.scale))
                            for entry in event.data["map"]:
                                match entry["type"]:
                                    case "tile":
                                        self.map.append(TileSprite.from_data(entry, self.scale))
                                    case "door":
                                        self.map.append(DoorSprite.from_data(entry, self.scale))
                                    case "wall":
                                        self.map.append(WallSprite.from_data(entry, self.scale))
                                    case "entry":
                                        self.map.append(EntryPointSprite.from_data(entry, self.scale))
                            print("setup Recived!")
                            print(self.smlist)
                            print(self.map)

                        if event.data["purpose"] == "readyup":
                            message = {"purpose" : "readytorecive"}
                            self.send(message)
                            print("ready sent!")

                        if event.data["purpose"] == "deploy_sm":
                            print(event.data["purpose"], event.data["entries"])
                            entrypoints = event.data["entries"]
                            marking = []
                            for point in entrypoints:
                                for sprite in self.map:
                                    if sprite.x == point["x"] and sprite.y == point["y"]:
                                        marking.append(sprite)
                            deploysm_marked_tiles = self.mark('red', marking)
                            self.state = Game_State.DEPLOY_SM
                            deploysm_to_place_sprites = self.smlist.copy()

                            x = 0
                            for sprite in deploysm_to_place_sprites:
                                print(sprite)
                                sprite.graphic_x = deploysm_top_sprites_start + x
                                sprite.graphic_y = 0
                                x += 1

                            wait = True
                            stateShift = True

                        if event.data["purpose"] == "continue":
                            self.state = Game_State.READY
                            wait = True
                            stateShift = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.disconnect()
                            self.state = Game_State.MAINMENU
                            wait = True
                            stateShift = True

                #start of the Game logic
                elif self.state == Game_State.DEPLOY_SM and not wait:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.disconnect()
                            self.state = Game_State.MAINMENU
                            wait = True
                            stateShift = True

                        if event.key == pygame.K_w:
                            for tile in self.map:
                                tile.move((0,1))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_d:
                            for tile in self.map:
                                tile.move((-1,0))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_s:
                            for tile in self.map:
                                tile.move((0,-1))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_a:
                            for tile in self.map:
                                tile.move((1,0))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if deploysm_deployButton.rect.collidepoint(pygame.mouse.get_pos()):
                            print(deploysm_selected_sprite, self.selected_tile)
                            if deploysm_selected_sprite != None:
                                print("Works1")
                                if deploysm_selected_sprite.pos_x == None and deploysm_selected_sprite.pos_y == None:
                                    print("Works2")
                                    if self.selected_tile != None:
                                        print("Works3")
                                        print(await_server_answer)
                                        message = {"purpose":"place", "tile":(self.selected_tile.x,self.selected_tile.y), "id":deploysm_selected_sprite.id}
                                        # if not await_server_answer:
                                        #     print(await_server_answer)
                                        self.send(message)
                                        #     await_server_answer = True

                        elif deploysm_rotateButton_right.rect.collidepoint(pygame.mouse.get_pos()):
                            if deploysm_selected_sprite != None:
                                if deploysm_selected_sprite.pos_x != None and deploysm_selected_sprite.pos_y != None:
                                    message = {
                                        "purpose": "rotate_model",
                                        "id":deploysm_selected_sprite.id,
                                        "phase": self.state.value,
                                        "dir": "right"
                                        }
                                    print(message, await_server_answer)
                                    # if not await_server_answer:
                                    #     print(await_server_answer)
                                    self.send(message)
                                    #     await_server_answer = True

                        elif deploysm_rotateButton_left.rect.collidepoint(pygame.mouse.get_pos()):
                            if deploysm_selected_sprite != None:
                                if deploysm_selected_sprite.pos_x != None and deploysm_selected_sprite.pos_y != None:
                                    message = {
                                        "purpose": "rotate_model",
                                        "id":deploysm_selected_sprite.id,
                                        "phase": self.state.value,
                                        "dir": "left"
                                        }
                                    print(message, await_server_answer)
                                    # if not await_server_answer:
                                    #     print(await_server_answer)
                                    self.send(message)
                                    #     await_server_answer = True

                        elif deploysm_finishButton.rect.collidepoint(pygame.mouse.get_pos()):
                            print("ready to move on")
                            if deploysm_to_place_sprites.__len__() == 0:
                                print("ready")
                                message = {
                                    "purpose": "finished_deploy",
                                    "phase":  self.state.value
                                    }
                                self.send(message)

                        else:
                            for tile in deploysm_marked_tiles:
                                if tile[0].rect.collidepoint(pygame.mouse.get_pos()):
                                    self.selected_tile = tile[0]
                                    print("clicked")
                                    print(self.selected_tile)
                                    stateShift = True
                        
                        for sprite in deploysm_to_place_sprites:
                            if sprite.rect.collidepoint(pygame.mouse.get_pos()):
                                print("smclick")
                                deploysm_selected_sprite = sprite
                                print(deploysm_selected_sprite)
                                stateShift = True

                    if event.type == pygame.USEREVENT:
                        if event.data["purpose"] == "game_update":
                            for tile in event.data["map"]:
                                pass
                            
                            for model in event.data["sm"]:
                                for marine in self.smlist:
                                    if model["id"] == marine.id:
                                        if model["pos_x"] != marine.pos_x or model["pos_y"] != marine.pos_y:
                                            print(model["pos_x"], marine.pos_x, model["pos_y"], marine.pos_y, model["face"], marine.face)
                                            for tile in self.map:
                                                if tile.x == model["pos_x"] and tile.y == model["pos_y"]:
                                                    marine.align(tile)
                                        if model["face"] != marine.face:
                                            marine.turn(model["face"])

                            if self.selected_tile != None:
                                for tile in deploysm_marked_tiles:
                                    if tile[0].x == self.selected_tile.x and tile[0].y == self.selected_tile.y:
                                        for model in self.smlist:
                                            if model.pos_x == tile[0].x and model.pos_y == tile[0].y:
                                                deploysm_marked_tiles.remove(tile)
                                                self.selected_tile = None
                                                break

                            if deploysm_selected_sprite in deploysm_to_place_sprites:
                                deploysm_to_place_sprites.remove(deploysm_selected_sprite)

                            stateShift = True
                            await_server_answer = False


                        if event.data["purpose"] == "wait":
                            self.state = Game_State.READY
                            wait = True
                            stateShift = True


                elif self.state == Game_State.DEPLOY_BL and not wait:

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.disconnect()
                            self.state = Game_State.MAINMENU
                            wait = True
                            stateShift = True

                        if event.key == pygame.K_w:
                            for tile in self.map:
                                tile.move((0,1))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_d:
                            for tile in self.map:
                                tile.move((-1,0))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_s:
                            for tile in self.map:
                                tile.move((0,-1))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_a:
                            for tile in self.map:
                                tile.move((1,0))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                    if deploybl_requested == False:
                        message = {
                            "purpose": "bl_request",
                        }
                        self.send(message)

                    if event.type == pygame.USEREVENT:
                        if event.data["purpose"] == "draw_blips":
                            for i in event.data["blips"]:
                                blip = BlipSprite.from_data(i, self.scale)
                                self.bllist.append(blip)
                                deploybl_to_place_sprites.append(blip)
                                

                                x = 0
                                for sprite in deploybl_to_place_sprites:
                                    print(sprite)
                                    sprite.graphic_x = deploybl_top_sprites_start + x
                                    sprite.graphic_y = 0
                                    x += 1

                elif self.state == Game_State.READY and not wait:

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.disconnect()
                            self.state = Game_State.MAINMENU
                            wait = True
                            stateShift = True

                        if event.key == pygame.K_w:
                            for tile in self.map:
                                tile.move((0,1))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_d:
                            for tile in self.map:
                                tile.move((-1,0))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_s:
                            for tile in self.map:
                                tile.move((0,-1))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                        if event.key == pygame.K_a:
                            for tile in self.map:
                                tile.move((1,0))
                                for model in self.smlist:
                                    if model.pos_x == tile.x and model.pos_y == tile.y:
                                        model.align(tile)
                                wait = True
                                stateShift = True

                    if event.type == pygame.USEREVENT:
                        if event.data["purpose"] == "game_update":
                            for tile in event.data["map"]:
                                pass
                            
                            for model in event.data["sm"]:
                                for marine in self.smlist:
                                    if model["id"] == marine.id:
                                        if model["pos_x"] != marine.pos_x or model["pos_y"] != marine.pos_y:
                                            print(model["pos_x"], marine.pos_x, model["pos_y"], marine.pos_y, model["face"], marine.face)
                                            for tile in self.map:
                                                if tile.x == model["pos_x"] and tile.y == model["pos_y"]:
                                                    marine.align(tile)
                                        
                                        if model["face"] != marine.face:
                                            marine.turn(model["face"])

                            stateShift = True

                        elif event.data["purpose"] == "place_bl":
                            if self.role == GameRole.GENSTEALER:

                                print(event.data["purpose"])

                                for tile in self.map:
                                    if isinstance(tile, EntryPointSprite):
                                        marking.append(tile)
                                        
                                deploybl_marked_tiles = self.mark('red', marking)
                                self.state = Game_State.DEPLOY_BL

                                wait = True
                                stateShift = True
                

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
                    config_slider.draw(self.screen)
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

                if self.state == Game_State.DEPLOY_SM:
                    self.screen.fill('black')

                    for tile in self.map:
                        tile.draw(self.screen)

                    for tile in deploysm_marked_tiles:
                        pygame.draw.rect(self.screen, tile[1], tile[0].rect, 3)

                    for marine in self.smlist:
                        if marine.pos_x != None:
                            marine.draw(self.screen)

                    if self.selected_tile != None:
                        pygame.draw.rect(self.screen, 'blue', self.selected_tile.rect, 4)

                    pygame.draw.rect(self.screen, 'black', self.button_bar)

                    deploysm_deployButton.draw(self.screen)
                    deploysm_rotateButton_right.draw(self.screen)
                    deploysm_rotateButton_left.draw(self.screen)
                    deploysm_finishButton.draw(self.screen)

                    for sprite in deploysm_to_place_sprites:
                        sprite.draw(self.screen)

                    if deploysm_selected_sprite != None:
                        print(deploysm_selected_sprite)
                        pygame.draw.rect(self.screen, 'blue', deploysm_selected_sprite.rect, 4)

                if self.state == Game_State.DEPLOY_BL:
                    self.screen.fill('black')

                    for tile in self.map:
                        tile.draw(self.screen)

                    for tile in deploybl_marked_tiles:
                        pygame.draw.rect(self.screen, tile[1], tile[0].rect, 3)

                    for blip in deploybl_to_place_sprites:
                        if blip.pos_x != None:
                            blip.draw(self.screen)

                    if self.selected_tile != None:
                        pygame.draw.rect(self.screen, 'blue', self.selected_tile.rect, 4)

                    pygame.draw.rect(self.screen, 'black', self.button_bar)

                    deploybl_deployButton.draw(self.screen)
                    deploybl_rotateButton_right.draw(self.screen)
                    deploybl_rotateButton_left.draw(self.screen)

                    for sprite in deploysm_to_place_sprites:
                        sprite.draw(self.screen)

                    if deploysm_selected_sprite != None:
                        print(deploysm_selected_sprite)
                        pygame.draw.rect(self.screen, 'blue', deploysm_selected_sprite.rect, 4)

                #teststate that will change, depending on the progress of the games development
                if self.state == Game_State.READY:
                    self.screen.fill('black')
                    for tile in self.map:
                        tile.draw(self.screen)
                    for tile in deploysm_marked_tiles:
                        pygame.draw.rect(self.screen, tile[1], tile[0].rect, 3)
                    for marine in self.smlist:
                        if marine.pos_x != None:
                            marine.draw(self.screen)
    
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
        timeout = 0
        self.send({"purpose": "disconnect"})
        while timeout < 60:
            timeout += 1
            if timeout == 60:
                print("Disconnection timed out!")
                self.running = False   # stoppe Empfangs-Thread
                self.client_socket.close()
                print("Verbindung getrennt")

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    if event.data["purpose"] == "disconnect":
                        self.running = False   # stoppe Empfangs-Thread
                        self.client_socket.close()
                        print("Verbindung getrennt")
    #     try:
    #         # Server informieren (optional)
    #         self.send({"purpose": "disconnect"})
    #     except:
    #         pass
    #     finally:
    #         self.running = False   # stoppe Empfangs-Thread
    #         self.client_socket.close()
    #         print("Verbindung getrennt")

    def send(self, message):
        self.client_socket.sendall((json.dumps(message) + "\n").encode())

    # def listen_to_server(self):
    #     while self.running:
    #         try:
    #             data = self.client_socket.recv(1024)
    #             if not data:
    #                 break
    #             message = json.loads(data.decode())

    #             match message["purpose"]:
    #                 case "lobby_joined":
    #                     self.players_in_lobby = []
    #                     for player in message["players"]:
    #                         self.players_in_lobby.append([player[0], GameRole[player[1]]])
    #                     print("Lobby joined:", self.players_in_lobby)
    #                 case "lobby_update":
    #                     self.players_in_lobby = []
    #                     for player in message["players"]:
    #                         self.players_in_lobby.append([player[0], GameRole[player[1]]])
    #                     print("Lobby joined:", self.players_in_lobby)
    #                 case "rolechange":
    #                     self.role = GameRole[message["role"]]
    #                 case "start_game":
    #                     print("Spiel startet!")

    #             pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"data" : message}))

    #         except Exception as e:
    #             print("Fehler in Lobby:", e)
    #             break

    def listen_to_server(self):
        buffer = ""   # Rest-Buffer für unvollständige Nachrichten
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                buffer += data.decode()

                # solange mindestens eine vollständige Nachricht im Buffer ist
                while "\n" in buffer:
                    raw_message, buffer = buffer.split("\n", 1)
                    if not raw_message.strip():
                        continue  # leere Nachrichten überspringen

                    try:
                        message = json.loads(raw_message)
                    except json.JSONDecodeError as e:
                        print("JSON-Fehler:", e, "bei Nachricht:", raw_message)
                        continue

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
                            print("Lobby update:", self.players_in_lobby)

                        case "rolechange":
                            self.role = GameRole[message["role"]]

                        case "start_game":
                            print("Spiel startet!")

                    # Event in pygame posten
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"data": message}))

            except Exception as e:
                print("Fehler in Lobby:", e)
                break
            
    def gameStat_lobby(self):
        test_server = Server()
        if test_server.start():
        #threading.Thread(target=test_server.start, args=(), daemon = True).start()
            self.is_host = True
            return True
        else:
            return False
    
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
    
    def mark(self, color, sprites):
        marked_tiles = []
        print("marking")
        if isinstance(sprites,list):
            print("liste")
            for sprite in sprites:
                marked_tiles.append((sprite, color))
        else:
            print("no list")
            marked_tiles.append((sprites, color))
        return(marked_tiles)

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