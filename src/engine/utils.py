import pygame
import os

class SpriteSheet:
    def __init__(self, filename):
        if not os.path.exists(filename):
            print(f"Aviso: Arquivo {filename} não encontrado. Usando placeholders.")
            self.sheet = None
            return
            
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Erro ao carregar spritesheet: {e}")
            self.sheet = None

    def get_image(self, x, y, width, height):
        if not self.sheet:
            # Cria um placeholder (rosa choque para destacar que falta algo)
            image = pygame.Surface((width, height))
            image.fill((255, 0, 255)) 
            # Desenha um pequeno quadrado preto para dar noção de animação/direção
            pygame.draw.rect(image, (0, 0, 0), (width//4, height//4, width//2, height//2))
            return image
            
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image
