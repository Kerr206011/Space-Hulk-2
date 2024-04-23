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
    
class Dice:
    def __init__(self, x, y) -> None:
        self.x
        self.y
        self.roll = False
        diceImage = [
        self.dice_1 = pygame.image.load("Pictures/Dice_Pictures/1.png")
        self.dice_2 = pygame.image.load("Pictures/Dice_Pictures/2.png")
        self.dice_3 = pygame.image.load("Pictures/Dice_Pictures/3.png")
        self.dice_4 = pygame.image.load("Pictures/Dice_Pictures/4.png")
        self.dice_5 = pygame.image.load("Pictures/Dice_Pictures/5.png")
        self.dice_6 = pygame.image.load("Pictures/Dice_Pictures/6.png")
        ]

    def display_random_dice(self, screen):
        random_side = random.randint(0, 5)
        screen.blit(dice_images[random_side], (self.x, self.y))
        pygame.display.update()

    def roll_dice(self, screen, button)
        while self.roll:
            self.display_random_dice(screen)
            time.sleep(0.2)  # Pause for a short duration between flashes
            
            if(button.draw(screen))
                # If any key is pressed, stop flashing
                self.roll = False
                break