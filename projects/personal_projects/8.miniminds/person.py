import pygame
import config

class Person:
    def __init__(self, name, person_type, image_file="imgs/player.png"):  # Set a default value for 'image_file'
        print("Person created")
        self.name = name
        self.type = person_type
        self.health = 10
        self.position = [0, 0]

        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(self.image, (config.SCALE, config.SCALE))

        self.rect = pygame.Rect(
            self.position[0] * config.SCALE,
            self.position[1] * config.SCALE,
            config.SCALE,
            config.SCALE
        )

    def render(self, screen):
        x, y = self.position
        rect = pygame.Rect(x * config.SCALE, y * config.SCALE, config.SCALE, config.SCALE)
        screen.blit(self.image, rect)



class PersonFactory:
    def __init__(self):
        self.count = 1

    def create_person(self, name, person_type):
        person = Person(name, person_type)
        self.count = self.count + 1
        return person
