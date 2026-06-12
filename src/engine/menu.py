import pygame

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_button = pygame.font.SysFont("Arial", 32)
        
        self.options = [
            {"label": "1. Smooth Mode (AI vs AI)", "mode": "SMOOTH"},
            {"label": "2. Step-by-Step Mode (AI vs AI)", "mode": "STEP"},
            {"label": "3. Human vs AI (Smooth)", "mode": "HUMAN_VS_AI"},
            {"label": "4. Tournament (batch headless)", "mode": "TOURNAMENT"},
            {"label": "5. Stats / Graphs", "mode": "STATS"}
        ]
        self.selected_index = 0

    def draw(self):
        self.screen.fill((30, 30, 30))
        
        title = self.font_title.render("BOMBERIA AI TESTBED", True, (255, 200, 0))
        title_rect = title.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title, title_rect)
        
        for i, opt in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected_index else (150, 150, 150)
            prefix = "> " if i == self.selected_index else "  "
            text = self.font_button.render(prefix + opt["label"], True, color)
            rect = text.get_rect(center=(self.width // 2, 300 + i * 60))
            self.screen.blit(text, rect)
            
        hint = self.font_button.render("Use Arrow Keys and ENTER to select", True, (100, 100, 100))
        self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height - 100)))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected_index]["mode"]
        return None
