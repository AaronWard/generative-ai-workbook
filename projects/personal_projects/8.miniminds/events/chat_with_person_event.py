import pygame
import config
from game_state import GameState


class ChatWithPersonEvent:

    def __init__(self, screen, game, person):
        self.screen = screen
        self.game = game
        self.person = person  # The person object with whom the player is chatting
        self.dialog = pygame.image.load("imgs/dialog.png")
        self.cut = 0
        self.max_cut = 2  # You can adjust this based on the number of dialog scenes you have
        self.font = pygame.font.Font(None, 36)


    def render(self):
        text = self.font.render(f"Chat with {self.person.name}", True, (255, 255, 255)) 

        if self.cut == 0:
            self.render_scene_0()
        elif self.cut == 1:
            self.render_scene_1()
        elif self.cut == 2:
            self.render_scene_2()

    def render_scene_0(self):
        self.screen.blit(self.dialog, (0, 300))
        # font = pygame.font.Font('fonts/PokemonGb.ttf', 20)
        img = self.font.render(f"Hi, I am {self.person.name}.", True, config.BLACK)
        self.screen.blit(img, (40, 400))

    def render_scene_1(self):
        self.screen.blit(self.dialog, (0, 300))
        # font = pygame.font.Font('fonts/PokemonGb.ttf', 20)
        img = self.font.render("How can I help you today?", True, config.BLACK)
        self.screen.blit(img, (40, 400))

    def render_scene_2(self):
        self.screen.blit(self.dialog, (0, 300))
        font = pygame.font.Font('fonts/PokemonGb.ttf', 20)
        img = font.render("Have a good day!", True, config.BLACK)
        self.screen.blit(img, (40, 400))

    def update(self):
        if self.cut > self.max_cut:
            self.game.event = None  # End the event when all dialog scenes are shown

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.game_state = GameState.ENDED
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.game_state = GameState.ENDED
                if event.key == pygame.K_RETURN:
                    self.cut = self.cut + 1  # Move to the next dialog scene when RETURN key is pressed
