import pygame
import config
from game_state import GameState
import ollama

class ChatWithPersonEvent:

    def __init__(self, screen, game, person):
        self.screen = screen
        self.game = game
        self.person = person  # The person object with whom the player is chatting
        self.dialog = pygame.image.load("imgs/dialog.png")
        self.font = pygame.font.Font(None, 36)
        self.input_active = True
        self.input_text = ''
        self.response = ''
        self.text_box = pygame.Rect(100, 550, 140, 32)  # Example position, adjust as needed
        self.base_font = pygame.font.Font(None, 32)

    def render(self):
        self.screen.blit(self.dialog, (0, 300))
        if self.input_active:
            self.render_input_box()
        else:
            self.render_response()

    def render_input_box(self):
        pygame.draw.rect(self.screen, config.WHITE, self.text_box, 0)
        text_surface = self.base_font.render(self.input_text, True, config.BLACK)
        self.screen.blit(text_surface, (self.text_box.x+5, self.text_box.y+5))
        self.text_box.w = max(100, text_surface.get_width()+10)

    def render_response(self):
        speech_bubble = self.font.render(self.response, True, config.BLACK)
        self.screen.blit(speech_bubble, (40, 400))  # Adjust positioning as needed

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.game_state = GameState.ENDED
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.game_state = GameState.ENDED
                elif event.key == pygame.K_RETURN and self.input_active:
                    self.input_active = False
                    self.chat_with_ollama()
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode

    def chat_with_ollama(self):
        response = ollama.chat(model='mistral:latest', messages=[
          {
            'role': 'user',
            'content': self.input_text,
            'temperature': 0.01,
          },
        ])
        self.response = response['message']['content']
