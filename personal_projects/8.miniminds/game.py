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
        self.person_to_chat_with = self.scan_around_player()  # Store the name of the person to chat with
        if self.person_to_chat_with:
            self.render_chat_button(self.person_to_chat_with) 
            

    def handle_events(self):
        """Process different events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.ENDED
            elif event.type == pygame.KEYDOWN:
                self.process_key_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.process_mouse_event(event)

    def process_key_event(self, event):
        """Handler for key strokes"""
        if event.key == pygame.K_ESCAPE:
            self.game_state = GameState.ENDED
        else:
            self.move_player(event.key)
    
    def process_mouse_event(self, event):
        """ Process click from mouse event """
        x, y = event.pos
        if hasattr(self, 'chat_button_rect') and self.chat_button_rect.collidepoint(x, y):
            self.chat_with_person()
            
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
            """Action call for when chat button is clicked"""
            if self.person_to_chat_with:
                # 1. Remove the chat button
                self.chat_button_rect = None  # This line already effectively removes the button

                # 2. Provide a text box for the message input
                input_box = pygame.Rect(100, 100, 140, 32)  # Adjust position and size as needed
                color_inactive = pygame.Color('lightskyblue3')
                color_active = pygame.Color('dodgerblue2')
                color = color_inactive
                active = False
                text = ''

                done = False
                while not done:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            done = True
                            pygame.quit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if input_box.collidepoint(event.pos):
                                active = not active
                            else:
                                active = False
                            color = color_active if active else color_inactive
                        if event.type == pygame.KEYDOWN:
                            if active:
                                if event.key == pygame.K_RETURN:
                                    done = True
                                elif event.key == pygame.K_BACKSPACE:
                                    text = text[:-1]
                                else:
                                    text += event.unicode

                    self.screen.fill((30, 30, 30))
                    txt_surface = self.dialog_font.render(text, True, color)
                    width = max(200, txt_surface.get_width()+10)
                    input_box.w = width
                    self.screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
                    pygame.draw.rect(self.screen, color, input_box, 2)

                    pygame.display.flip()

                # 3. Use ollama to interact with the LLM
                response = ollama.chat(model='mistral:latest', messages=[
                    {
                        'role': 'user',
                        'content': text,
                        'temperature': 0.01,
                    },
                ])

                # 4. Display the response in a speech bubble
                dialog_img = pygame.image.load('imgs/dialog.png')  # Load the speech bubble image
                response_text = response['message']['content']
                wrapped_text = self.wrap_text(response_text, 300)  # Assuming a width of 220 pixels for text
                dialog_surface = pygame.Surface((dialog_img.get_width(), dialog_img.get_height()))
                dialog_surface.blit(dialog_img, (0, 0))
                y_offset = 10  # Start drawing text slightly below the top of the bubble
                for line in wrapped_text:
                    text_surface = self.dialog_font.render(line, True, (0, 0, 0))
                    dialog_surface.blit(text_surface, (10, y_offset))
                    y_offset += self.dialog_font.get_height() + 2  # Move down for the next line

                # Position the speech bubble above the NPC
                npc_x, npc_y = self.person_to_chat_with.position
                bubble_x = npc_x * config.TILE_SIZE - dialog_surface.get_width() / 2
                bubble_y = npc_y * config.TILE_SIZE - dialog_surface.get_height() - 20
                self.screen.blit(dialog_surface, (bubble_x, bubble_y))

                pygame.display.flip()
                pygame.time.wait(5000)

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