import random
import string
from game import Game

class GameManager:
    def __init__(self):
        self.games = []
        self.existing_codes = set()

    def create_game(self):
        """ Creates and adds a new game with unique game code """
        code = self.generate_code()
        game = Game(code)
        self.games.append(game)
        self.existing_codes.add(code)
        return game

    def generate_code(self):
        """ Generates a unique and random game code """
        while True:
            code = ''.join(random.choices(string.ascii_uppercase, k=4))
            if code not in self.existing_codes:
                return code