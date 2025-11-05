from player import Player

class Game:
    def __init__(self, code):
        self.code = code
        self.players = []
        self.existing_player_names = set()

    def add_player(self, player_name):
        """ Creates and adds a new player with unique name """
        normalized_name = player_name.lower()
        if normalized_name in self.existing_player_names:
            raise ValueError(f"A player with the name {player_name} already exists")
        player = Player(player_name)
        self.players.append(player)
        self.existing_player_names.add(normalized_name)
        return player