import pygame
import config
import random
import ollama
from player import Player
from person import Person  
from game_state import GameState
from game_view.map import Map

from events.chat_with_person_event import ChatWithPersonEvent

class Game:
    """
    Game 
    
    """
    def __init__(self, screen):
        self.screen = screen
        self.objects = []
        self.game_state = GameState.NONE
        self.map = Map(screen) 
        self.people = []
        self.dialog_font = pygame.font.Font(None, 18) 
        
        self.active_text_input = False
        self.text_input = ''
        self.text_input_color = pygame.Color('dodgerblue2')
        self.text_input_rect = pygame.Rect(100, config.SCREEN_HEIGHT - 40, config.SCREEN_WIDTH - 200, 32)
        self.message_response = None
        self.message_timer = 0

    def set_up(self):
        """Set the player on the map"""
        player = Player(10, 10)
        self.player = player
        self.objects.append(player)
        self.game_state = GameState.RUNNING
    
    def load(self, file_name):
        """Generate randomized map"""
        self.map.load(file_name) 
        self.place_people_on_map()  
        
    def update(self):
        """Called by main"""
        self.screen.fill(config.BLACK)
        self.handle_events()
        self.map.render(self.player, self.objects)
        self.person_to_chat_with = self.scan_around_player()  # Store the person object to chat with
        if self.person_to_chat_with:
            self.render_chat_button(f"{self.person_to_chat_with.name}") 
        if self.active_text_input:
            self.render_text_input()  # New method to render text input
        if self.message_response and pygame.time.get_ticks() < self.message_timer:
            self.render_message_response()
        else:
            self.message_response = None  # Reset message when timer expires

    def render_text_input(self):
        txt_surface = self.dialog_font.render(self.text_input, True, self.text_input_color)
        pygame.draw.rect(self.screen, self.text_input_color, self.text_input_rect, 2)
        self.screen.blit(txt_surface, (self.text_input_rect.x+5, self.text_input_rect.y+5))

    def render_message_response(self):
        if not self.person_to_chat_with:
            return
        npc_x, npc_y = self.person_to_chat_with.position
        bubble_x = npc_x * config.TILE_SIZE
        bubble_y = npc_y * config.TILE_SIZE - 100  # Adjust based on your NPC's height and bubble size
        for i, line in enumerate(self.message_response):
            text_surface = self.dialog_font.render(line, True, (0, 0, 0))
            self.screen.blit(text_surface, (bubble_x, bubble_y + i*20))  # Adjust spacing and positioning as needed


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.ENDED
            elif event.type == pygame.KEYDOWN:
                if self.active_text_input:
                    if event.key == pygame.K_RETURN:
                        print(f"Input: {self.text_input}")
                        self.chat_with_person()
                        self.active_text_input = False
                        self.text_input = ''  # Reset text input
                    elif event.key == pygame.K_BACKSPACE:
                        self.text_input = self.text_input[:-1]
                    else:
                        self.text_input += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.ENDED
                    else:
                        self.move_player(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.process_mouse_event(event)


    def process_key_event(self, event):
        """Handler for key strokes"""
        if event.key == pygame.K_ESCAPE:
            self.game_state = GameState.ENDED
        else:
            self.move_player(event.key)
    
    def process_mouse_event(self, event):
        x, y = event.pos
        if hasattr(self, 'chat_button_rect') and self.chat_button_rect.collidepoint(x, y):
            self.active_text_input = True

            
    def move_player(self, key):
        """Move sprite based on movements"""
        x_change, y_change = config.MOVEMENTS.get(key, (0, 0))
        new_x, new_y = self.player.position[0] + x_change, self.player.position[1] + y_change
        if self.can_move_to_position(new_x, new_y):
            self.player.update_position(x_change, y_change)
            
    def can_move_to_position(self, x, y):
        """Only allow movements on grass tiles"""
        if 0 <= x < len(self.map.map_array[0]) and 0 <= y < len(self.map.map_array):
            if self.map.map_array[y][x] == config.MAP_TILE_GRASS:
                return not any(person.position == [x, y] for person in self.people)
        return False
        
    def place_people_on_map(self):
        """Place NPCs and player on map"""
        grass_positions = [(x, y) for y, row in enumerate(self.map.map_array)
                           for x, tile in enumerate(row) if tile == config.MAP_TILE_GRASS]
        
        for name, details in config.NPC_CONFIGS.items():
            if grass_positions:  # Check if there are available grass positions
                position = random.choice(grass_positions)
                grass_positions.remove(position)  # Remove the chosen position from available positions
                
                person = Person(name, details["personality_type"], details["image_file"])
                person.position = list(position)
                self.objects.append(person)
                self.people.append(person)  # You might want to keep track of the people
            else:
                print(f"Error: Could not place {name} on grass")
            
    def scan_around_player(self):
        """Show chat buttong if player is next to NPC"""
        x, y = self.player.position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < len(self.map.map_array[0]) and 0 <= new_y < len(self.map.map_array):
                    for person in self.people:
                        if person.position == [new_x, new_y]:
                            if dx == 0 and dy == 0:  # This is the player's position
                                continue
                            return person  # Return the person object around the player
        return None
        
    def place_person_on_grass(self):
        """Only place NPC or player on grass tiles"""
        for y_index, row in enumerate(self.map.map_array):
            for x_index, tile in enumerate(row):
                if tile == config.MAP_TILE_GRASS:
                    return [x_index, y_index]
        return None  # Suitable position not found
            
    def render_chat_button(self, person_name):
        """Show chat button"""
        font = pygame.font.Font(None, 36)
        text = font.render(f"Chat with {person_name}", True, (255, 255, 255))  # Use the person's name in the button text
        button_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 20))
        pygame.draw.rect(self.screen, (0, 0, 0), button_rect)
        self.screen.blit(text, button_rect)
        self.chat_button_rect = button_rect
        
    # def chat_with_person(self):
    #     """Action call for when chat button is clicked"""
    #     if self.person_to_chat_with:
    #         # Assuming person_to_chat_with is a Person object, not just the name
    #         self.chat_button_rect = None
    #         self.event = ChatWithPersonEvent(self.screen, self, self.person_to_chat_with)
    #         print(f"You are now chatting with {self.person_to_chat_with.name}.")  


    def chat_with_person(self):
        # Assuming ollama's chat call is synchronous and blocking; if not, adjust accordingly
        response = ollama.chat(model='mistral:latest', messages=[
            {
                'role': 'user',
                'content': self.text_input,
                'temperature': 0.01,
            },
        ])
        self.display_message_response(response['message']['content'])

    def display_message_response(self, text):
        self.message_response = self.wrap_text(text, 220)  # Adjust width as needed
        self.message_timer = pygame.time.get_ticks() + 5000  # Display for 5 seconds


    def wrap_text(self, text, width):
        """Wrap text for drawing within a certain width."""
        words = text.split()
        lines = []
        while words:
            line = ''
            while words and self.dialog_font.size(line + words[0])[0] < width:
                line += (words.pop(0) + ' ')
            lines.append(line)
        return lines