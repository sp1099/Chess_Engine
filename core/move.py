from constants import SQUARE_TABLE

class Move():

    def __init__(self, start_square, end_square, promotion_piece=None, move_type=None):

        self.start_square = start_square
        self.end_square = end_square
        self.promotion_piece = promotion_piece
        self.move_type = move_type

    def __repr__(self):
        return f"{self.move_type}: {SQUARE_TABLE[self.start_square]} -> {SQUARE_TABLE[self.end_square]} | ({self.start_square} -> {self.end_square})"