import pygame
import sys
import threading
import random
import time

class Button():
    def __init__(self, x, y, image, scale) -> None:
        self.scale = scale
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (int(self.width * scale), int(self.height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.prev_mouse_state = False

    def change_picture(self, image):
        self.image = pygame.transform.scale(image, (int(self.width * self.scale), int(self.height * self.scale)))

    def show(self, surface, addImage = None):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        if addImage != None:
            image = pygame.transform.scale(addImage, (int(self.width * self.scale), int(self.height * self.scale)))
            surface.blit(image, (self.rect.x, self.rect.y))

    def draw(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()
        #get mouse state
        mouse_state = pygame.mouse.get_pressed()[0] == 1

        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            # Check if mouse button is pressed down
            if mouse_state and not self.prev_mouse_state:
                self.clicked = True

         # Check if mouse button is released
        if not mouse_state and self.prev_mouse_state:
            if self.clicked:
                action = True
            self.clicked = False

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

         # Update previous mouse state
        self.prev_mouse_state = mouse_state

        return action

    def safedraw(self, surface):    #only returns True if the Mouse is released and on the Button
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()
        #get mouse state
        mouse_state = pygame.mouse.get_pressed()[0] == 1

        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            # Check if mouse button is pressed down
            if mouse_state and not self.prev_mouse_state:
                self.clicked = True

         # Check if mouse button is released
        if not mouse_state and self.prev_mouse_state:
            if self.clicked:
                if(self.rect.collidepoint(pos)):
                    action = True
            self.clicked = False

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

         # Update previous mouse state
        self.prev_mouse_state = mouse_state

        return action

    def hover(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            action = True

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action
    
    def move_button(self, direction):
        pos = self.rect.topleft
        x = pos[0] + direction[0]
        y = pos[1] + direction[1]
        self.rect.topleft = (x, y)
    
class Dice:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.face = 1
        self.diceImage = [
        pygame.image.load("Pictures/Dice_Pictures/1.png"),
        pygame.image.load("Pictures/Dice_Pictures/2.png"),
        pygame.image.load("Pictures/Dice_Pictures/3.png"),
        pygame.image.load("Pictures/Dice_Pictures/4.png"),
        pygame.image.load("Pictures/Dice_Pictures/5.png"),
        pygame.image.load("Pictures/Dice_Pictures/6.png")
        ]
        self.picture = self.diceImage[0]
        self.rect = self.picture.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.prev_mouse_state = False

    def roll_dice(self, screen, frames = 15, sleepTime = 0.1):
        a = 0
        while a < frames:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        a = frames-1
            b = random.randint(0, 5)
            self.face = b + 1
            self.picture = self.diceImage[b]
            a +=1
            screen.blit(self.picture, (self.x, self.y))
            pygame.display.update(self.rect)
            time.sleep(sleepTime)

    def show_result(self, screen):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()
        #get mouse state
        mouse_state = pygame.mouse.get_pressed()[0] == 1

        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            # Check if mouse button is pressed down
            if mouse_state and not self.prev_mouse_state:
                self.clicked = True

         # Check if mouse button is released
        if not mouse_state and self.prev_mouse_state:
            if self.clicked:
                action = True
            self.clicked = False

        #draw button on screen
        screen.blit(self.picture, (self.rect.x, self.rect.y))

         # Update previous mouse state
        self.prev_mouse_state = mouse_state

        return action

class ActionField:

    def __init__(self, width, height, top, left):
        self.slots = []
        self.rect = pygame.Rect(left, top, width, height)
        self.color = 'blue'
        self.fields = []

    def align(self, pos):
        self.rect.topleft = pos

    def align_buttons(self, buttons:list[Button]):
        """
        Method to add Buttons to the Actionbar and distribute them.

        Args:
            buttons: list[Button]

        Returns:
            None.
        """
        i = 0
        for button in buttons:
            button.rect.topleft = self.slots[i]
            self.fields.append(button)
            i +=1

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        for button in self.fields:
            button.draw(screen)
        pygame.display.flip()