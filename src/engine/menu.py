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
        self.font_row    = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_sub    = pygame.font.SysFont("Arial", 22)
        self.font_option = pygame.font.SysFont("Arial", 24)
        self.font_hint   = pygame.font.SysFont("Arial", 20)
        self.row_index   = 0
        self.selections  = list(defaults) if defaults else [0] * len(rows)

    def draw(self):
        self.screen.fill((30, 30, 30))
        title = self.font_title.render("== CONFIGURE GAME ==", True, (255, 200, 0))
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 70)))

        TITLE_BOTTOM = 120
        HINTS_TOP    = self.height - 50
        available    = HINTS_TOP - TITLE_BOTTOM
        row_spacing  = min(100, available // max(len(self.rows), 1))
        row_start_y  = TITLE_BOTTOM + row_spacing // 2

        start_x = self.width // 2 + 10

        for r_idx, row in enumerate(self.rows):
            row_y   = row_start_y + r_idx * row_spacing
            is_sub  = row.get("sub", False)
            focused = (self.row_index == r_idx)

            label_font  = self.font_sub if is_sub else self.font_row
            label_color = (255, 255, 255) if focused else ((160, 160, 160) if is_sub else (150, 150, 150))
            label_x     = self.width // 2 - (30 if is_sub else 20)
            label_surf  = label_font.render(row["label"] + ":", True, label_color)
            self.screen.blit(label_surf, label_surf.get_rect(midright=(label_x, row_y)))

            n_opts       = len(row["options"])
            chip_spacing = min(160, (self.width - start_x - 10) // n_opts)

            for o_idx, opt in enumerate(row["options"]):
                selected  = (self.selections[r_idx] == o_idx)
                text      = f"< {opt} >" if selected else f"  {opt}  "
                color     = (255, 255, 0) if selected else ((200, 200, 200) if focused else (110, 110, 110))
                opt_surf  = self.font_option.render(text, True, color)
                cx        = start_x + o_idx * chip_spacing + chip_spacing // 2
                self.screen.blit(opt_surf, opt_surf.get_rect(center=(cx, row_y)))

        hint = self.font_hint.render(
            "LEFT/RIGHT: change option    UP/DOWN: move row    ENTER: start    ESC: back",
            True, (100, 100, 100)
        )
        self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height - 25)))

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
