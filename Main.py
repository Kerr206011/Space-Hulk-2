# from Board import *
# from Models import *
# from Game import *

# game = Game()

from MultiplayerClassClient import *
from MultiplayerClassServer import *

server = Server()
threading.Thread(target=server.start(), args=()).start()

pygame.time.wait(20)

client = Test_Client(name='Player2')
client.connect()