from abc import ABC, abstractmethod


# an abstract player class
class player(ABC):
    @abstractmethod
    def __init__(self, bitboards, color):
        self.bitboards = bitboards
        self.color = color

    @abstractmethod
    def update_bitboards(self, bitboards):
        pass

    @abstractmethod
    def get_player_move(self):
        pass
