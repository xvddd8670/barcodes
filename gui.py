import pygame
import pygame_gui



class Button:
    def __init__(self, coord_x, coord_y, btn_width, btn_height, btn_text, manager):
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.btn_width = btn_width
        self.btn_height = btn_height
        self.btn_text = btn_text
        ##
        self.button_rectangle = pygame.Rect((self.coord_x, self.coord_y), (self.btn_width, self.btn_height))
        self.button = pygame_gui.elements.UIButton(
            relative_rect=self.button_rectangle,
            text=self.btn_text,
            manager=manager)
        self.hide_show = True

class Counter:
    def __init__(self, coord_x, coord_y, counter_width, counter_height, visible_counter,  manager):
        #main vars
        self.counter = 0
        #coords n sizes
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.counter_width = counter_width
        self.counter_height = counter_height
        self.block_height = self.counter_height/3
        self.counter_block_coord_y = self.coord_y+self.block_height
        self.counter_block_height = self.counter_height/3
        #button minus
        self.button_plus = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.coord_x, self.coord_y), (self.counter_width, self.counter_height/3)),
            text='+',
            manager=manager)
        #counter
        self.counter_text_size = int(self.counter_height/3)
        self.counter_text_font = pygame.font.Font(None, self.counter_text_size)
        #button plus
        self.button_minus = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.coord_x, self.coord_y+(self.block_height*2)), (self.counter_width, self.counter_height/3)),
            text='-',
            manager=manager)
        self.visible_counter = visible_counter
    #render def
    def render(self, screen):
        pygame.draw.rect(screen,
                         (50, 50, 50),
                         pygame.Rect(self.coord_x+2,
                                     self.counter_block_coord_y,
                                     self.counter_width-4,
                                     self.counter_block_height))
        if self.visible_counter == True:
            counter_text = self.counter_text_font.render(str(self.counter), True, (255, 50, 50))
            screen.blit(counter_text,
                        (self.coord_x+(self.counter_width/3),
                         self.counter_block_coord_y+(self.block_height/4)))










