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


class AgentSelectMenu:
    def __init__(self, screen, rows, defaults=None):
        self.screen = screen
        self.rows = rows
        self.width, self.height = screen.get_size()
        self.font_title  = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_row    = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_option = pygame.font.SysFont("Arial", 28)
        self.font_hint   = pygame.font.SysFont("Arial", 22)
        self.row_index   = 0
        self.selections  = list(defaults) if defaults else [0] * len(rows)

    def draw(self):
        self.screen.fill((30, 30, 30))
        title = self.font_title.render("== CONFIGURE GAME ==", True, (255, 200, 0))
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 100)))

        ROW_START_Y = 220
        ROW_SPACING = 120
        for r_idx, row in enumerate(self.rows):
            row_y = ROW_START_Y + r_idx * ROW_SPACING
            label_color = (255, 255, 255) if r_idx == self.row_index else (150, 150, 150)
            label_surf = self.font_row.render(row["label"] + ":", True, label_color)
            self.screen.blit(label_surf, label_surf.get_rect(midright=(self.width // 2 - 20, row_y)))

            CHIP_SPACING = 160
            start_x = self.width // 2 + 10
            for o_idx, opt in enumerate(row["options"]):
                selected = (self.selections[r_idx] == o_idx)
                focused  = (self.row_index == r_idx)
                text  = f"< {opt} >" if selected else f"  {opt}  "
                color = (255, 255, 0) if selected else ((200, 200, 200) if focused else (120, 120, 120))
                opt_surf = self.font_option.render(text, True, color)
                cx = start_x + o_idx * CHIP_SPACING + CHIP_SPACING // 2
                self.screen.blit(opt_surf, opt_surf.get_rect(center=(cx, row_y)))

        hint = self.font_hint.render(
            "LEFT/RIGHT: change option    UP/DOWN: move row    ENTER: start    ESC: back",
            True, (100, 100, 100)
        )
        self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height - 60)))

    def handle_input(self):
        """Returns None | "BACK" | "QUIT" | config dict"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "BACK"
                elif event.key == pygame.K_UP:
                    self.row_index = (self.row_index - 1) % len(self.rows)
                elif event.key == pygame.K_DOWN:
                    self.row_index = (self.row_index + 1) % len(self.rows)
                elif event.key == pygame.K_LEFT:
                    n = len(self.rows[self.row_index]["options"])
                    self.selections[self.row_index] = (self.selections[self.row_index] - 1) % n
                elif event.key == pygame.K_RIGHT:
                    n = len(self.rows[self.row_index]["options"])
                    self.selections[self.row_index] = (self.selections[self.row_index] + 1) % n
                elif event.key == pygame.K_RETURN:
                    return self._build_config()
        return None

    def _build_config(self):
        return {row["key"]: row["options"][self.selections[i]]
                for i, row in enumerate(self.rows)}
