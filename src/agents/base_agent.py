class BaseAgent:
    def __init__(self, player_id):
        self.player_id = player_id
        
    def get_action(self, game_state):
        """
        Deve retornar uma ação baseada no estado do jogo.
        Ações possíveis: UP, DOWN, LEFT, RIGHT, PLACE_BOMB, IDLE
        """
        raise NotImplementedError
