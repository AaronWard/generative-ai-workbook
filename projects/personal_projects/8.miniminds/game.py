import pygame
import config
import random
from player import Player
from person import Person  
from game_state import GameState
from game_view.map import Map

from events.chat_with_person_event import ChatWithPersonEvent

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.objects = []
        self.game_state = GameState.NONE
        self.map = Map(screen) 
        self.people = []
        
    def set_up(self):
        player = Player(10, 10)
        self.player = player
        self.objects.append(player)
        self.game_state = GameState.RUNNING
    
    def load(self, file_name):
        self.map.load(file_name)  # This will now generate the map if it doesn't exist
        self.place_people_on_map()  
        
    def update(self):
        self.screen.fill(config.BLACK)
        self.handle_events()
        self.map.render(self.player, self.objects)
        self.person_to_chat_with = self.scan_around_player()  # Store the name of the person to chat with
        if self.person_to_chat_with:
            self.render_chat_button(self.person_to_chat_with) 

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.ENDED
            elif event.type == pygame.KEYDOWN:
                self.process_key_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.process_mouse_event(event)
                
    def process_key_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self.game_state = GameState.ENDED
        else:
            self.move_player(event.key)
    
    def process_mouse_event(self, event):
        x, y = event.pos
        if hasattr(self, 'chat_button_rect') and self.chat_button_rect.collidepoint(x, y):
            self.chat_with_person()
            
    def move_player(self, key):
        x_change, y_change = config.MOVEMENTS.get(key, (0, 0))
        new_x, new_y = self.player.position[0] + x_change, self.player.position[1] + y_change
        if self.can_move_to_position(new_x, new_y):
            self.player.update_position(x_change, y_change)
            
    def can_move_to_position(self, x, y):
        if 0 <= x < len(self.map.map_array[0]) and 0 <= y < len(self.map.map_array):
            if self.map.map_array[y][x] == config.MAP_TILE_GRASS:
                return not any(person.position == [x, y] for person in self.people)
        return False
        
    def place_people_on_map(self):
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
        x, y = self.player.position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < len(self.map.map_array[0]) and 0 <= new_y < len(self.map.map_array):
                    for person in self.people:
                        if person.position == [new_x, new_y]:
                            if dx == 0 and dy == 0:  # This is the player's position
                                continue
                            return person.name  # Return the name of the person around the player
        return None
        
    def place_person_on_grass(self):
        for y_index, row in enumerate(self.map.map_array):
            for x_index, tile in enumerate(row):
                if tile == config.MAP_TILE_GRASS:
                    return [x_index, y_index]
        return None  # Suitable position not found
            
    def render_chat_button(self, person_name):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Chat with {person_name}", True, (255, 255, 255))  # Use the person's name in the button text
        button_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 20))
        pygame.draw.rect(self.screen, (0, 0, 0), button_rect)
        self.screen.blit(text, button_rect)
        self.chat_button_rect = button_rect
        
    def chat_with_person(self):
        if self.person_to_chat_with:
            # self.event = ChatWithPersonEvent(self.screen, self, self.person_to_chat_with)
            print(f"You are now chatting with {self.person_to_chat_with}.")  # Use the stored person's name

    def process_mouse_event(self, event):
        x, y = event.pos
        if hasattr(self, 'chat_button_rect') and self.chat_button_rect.collidepoint(x, y):
            person = self.get_person_near_player()  # Assume you have a method to get the person near the player
            if person:
                self.event = ChatWithPersonEvent(self.screen, self, person)