from enum import Enum

from .player import Player


class Color(Enum):
    NONE = 'none'
    BLUE = 'blue'
    RED = 'red'


class Game:
    """
    A Baby soccer/foosbal game representation with two sides, blue and red.
    """
    def __init__(self, max_points=8):
        self.player_blue = Player(Color.BLUE)
        self.player_red = Player(Color.RED)

        self.game_finished = False

        self.max_points = max_points

    def goal(self, scorer):
        """
        Records a goal for the specified player and
        check if he has won the game.
        """
        if scorer.score < self.max_points:
            scorer.score += 1
        if scorer.score == self.max_points:
            self.win(scorer)

    def win(self, winner):
        """
        Called when one of the player reaches the maxpoint
        """
        if winner.color == Color.BLUE:
            print('Blue wins the game !')
        elif winner.color == Color.RED:
            print('Red wins the game !')

    def reset(self):
        """
        Resets the scores of both players.
        """
        self.player_blue.score = 0
        self.player_red.score = 0

        print('Game has been reset.')
