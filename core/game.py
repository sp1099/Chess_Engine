import numpy as np

from constants import *
from move import Move
from utils.bitboard_operations import *

class Game():

    def __init__(self):

        self.color = COLOR_WHITE

        self.piece_bitboards = {
            "white_pawn": np.uint64(0),
            "white_knight": np.uint64(0),
            "white_bishop": np.uint64(0),
            "white_rook": np.uint64(0),
            "white_queen": np.uint64(0),
            "white_king": np.uint64(0),

            "black_pawn": np.uint64(0),
            "black_knight": np.uint64(0),
            "black_bishop": np.uint64(0),
            "black_rook": np.uint64(0),
            "black_queen": np.uint64(0),
            "black_king": np.uint64(0)
        }
        self.init_pieces()

    def init_pieces(self):
        self.piece_bitboards["white_rook"] = set_bitboard_bit(0, self.piece_bitboards["white_rook"])
        self.piece_bitboards["white_rook"] = set_bitboard_bit(7, self.piece_bitboards["white_rook"])
        self.piece_bitboards["white_knight"] = set_bitboard_bit(1, self.piece_bitboards["white_knight"])
        self.piece_bitboards["white_knight"] = set_bitboard_bit(6, self.piece_bitboards["white_knight"])
        self.piece_bitboards["white_bishop"] = set_bitboard_bit(2, self.piece_bitboards["white_bishop"])
        self.piece_bitboards["white_bishop"] = set_bitboard_bit(5, self.piece_bitboards["white_bishop"])
        self.piece_bitboards["white_queen"] = set_bitboard_bit(3, self.piece_bitboards["white_queen"])
        self.piece_bitboards["white_king"] = set_bitboard_bit(4, self.piece_bitboards["white_king"])

        self.piece_bitboards["black_rook"] = set_bitboard_bit(63, self.piece_bitboards["black_rook"])
        self.piece_bitboards["black_rook"] = set_bitboard_bit(56, self.piece_bitboards["black_rook"])
        self.piece_bitboards["black_knight"] = set_bitboard_bit(62, self.piece_bitboards["black_knight"])
        self.piece_bitboards["black_knight"] = set_bitboard_bit(57, self.piece_bitboards["black_knight"])
        self.piece_bitboards["black_bishop"] = set_bitboard_bit(61, self.piece_bitboards["black_bishop"])
        self.piece_bitboards["black_bishop"] = set_bitboard_bit(58, self.piece_bitboards["black_bishop"])
        self.piece_bitboards["black_queen"] = set_bitboard_bit(59, self.piece_bitboards["black_queen"])
        self.piece_bitboards["black_king"] = set_bitboard_bit(60, self.piece_bitboards["black_king"])

        for i in range(8, 16):
            self.piece_bitboards["white_pawn"] = set_bitboard_bit(i, self.piece_bitboards["white_pawn"])
            self.piece_bitboards["black_pawn"] = set_bitboard_bit(63 - i, self.piece_bitboards["black_pawn"])


        # DEBUG
        self.piece_bitboards["white_rook"] = set_bitboard_bit(35, self.piece_bitboards["white_rook"])


    def pretty_print_board(self):

        pretty_board = [
            ".", ".", ".", ".", ".", ".", ".", ".",
            ".", ".", ".", ".", ".", ".", ".", ".",
            ".", ".", ".", ".", ".", ".", ".", ".",
            ".", ".", ".", ".", ".", ".", ".", ".",
            ".", ".", ".", ".", ".", ".", ".", ".",
            ".", ".", ".", ".", ".", ".", ".", ".",
            ".", ".", ".", ".", ".", ".", ".", ".",
            ".", ".", ".", ".", ".", ".", ".", "."
        ]

        for piece_type, piece_bitboard in self.piece_bitboards.items():
            for square_index in range(64):
                if np.bitwise_and(piece_bitboard, (np.uint64(1) << np.uint8(square_index))):
                    pretty_board[square_index] = PIECE_UNICODE[piece_type]

        for rank in range(7, -1, -1):
            for file in range(8):
                print(pretty_board[8 * rank + file], end=" ")
            print()
        print()

        # occupancy_board = np.zeros(64, np.uint64)
        # for piece_bitboard in self.piece_bitboards.values():
        #     occupancy_board = np.bitwise_or(occupancy_board, piece_bitboard)

        # self.print_bitboard(occupancy_board)


    def generate_moves(self):
        pseudo_legal_moves = []

        pseudo_legal_moves.extend(self.generate_pawn_moves())
        pseudo_legal_moves.extend(self.generate_knight_moves())
        pseudo_legal_moves.extend(self.generate_king_moves())
        pseudo_legal_moves.extend(self.generate_bishop_moves())
        pseudo_legal_moves.extend(self.generate_rook_moves())
        pseudo_legal_moves.extend(self.generate_queen_moves())
            
        # Make pseudo legal moves and test for king checks
        legal_moves = []
        for move in pseudo_legal_moves:
            if self.check_pseudo_move(move):
                legal_moves.append(move)

        return legal_moves

    def generate_pawn_moves(self):
        occupancy_white = np.uint64(0)
        occupancy_black = np.uint64(0)

        pawn_moves = []
        pawn_attacks = []

        for piece_type, bitboard in self.piece_bitboards.items():
            if "white" in piece_type:
                occupancy_white = np.bitwise_or(occupancy_white, bitboard)
            else:
                occupancy_black = np.bitwise_or(occupancy_black, bitboard)

        if self.color == COLOR_WHITE:
            for pawn_square in range(64):
                pawn_moves.extend(self.generate_white_pawn_moves(pawn_square, np.bitwise_or(occupancy_white, occupancy_black)))
                pawn_attacks.extend(self.generate_white_pawn_attacks(pawn_square, occupancy_black))
        else:
            for pawn_square in range(64):
                pawn_moves.extend(self.generate_black_pawn_moves(pawn_square, np.bitwise_or(occupancy_white, occupancy_black)))
                pawn_attacks.extend(self.generate_black_pawn_attacks(pawn_square, occupancy_white))

        return (pawn_moves + pawn_attacks)

    def generate_white_pawn_moves(self, pawn_square, board_occupancy):
        pawn_moves = []
        if np.bitwise_and(self.piece_bitboards["white_pawn"], (np.uint64(1) << np.uint8(pawn_square))):
            move_bitboard = np.bitwise_and(PAWN_MOVES_WHITE[pawn_square], np.bitwise_not(board_occupancy))
            for move_square in range(64):
                if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                    pawn_moves.append(Move(start_square=pawn_square, end_square=move_square, move_type="WHITE PAWN MOVE"))

        if len(pawn_moves) == 1:
            if abs(pawn_moves[0].start_square - pawn_moves[0].end_square) == 16:
                pawn_moves = []

        return pawn_moves

    def generate_white_pawn_attacks(self, pawn_square, occupancy_black):
        pawn_attacks = []
        if np.bitwise_and(self.piece_bitboards["white_pawn"], (np.uint64(1) << np.uint8(pawn_square))):
            move_bitboard = np.bitwise_and(PAWN_ATTACKS_WHITE[pawn_square], occupancy_black)
            for move_square in range(64):
                if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                    pawn_attacks.append(Move(start_square=pawn_square, end_square=move_square, move_type="WHITE PAWN ATTACK"))

        return pawn_attacks

    def generate_black_pawn_moves(self, pawn_square, board_occupancy):
        pawn_moves = []
        if np.bitwise_and(self.piece_bitboards["black_pawn"], (np.uint64(1) << np.uint8(pawn_square))):
            move_bitboard = np.bitwise_and(PAWN_MOVES_BLACK[pawn_square], np.bitwise_not(board_occupancy))
            for move_square in range(64):
                if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                    pawn_moves.append(Move(start_square=pawn_square, end_square=move_square, move_type="BLACK PAWN MOVE"))

        if len(pawn_moves) == 1:
            if abs(pawn_moves[0].start_square - pawn_moves[0].end_square) == 16:
                pawn_moves = []

        return pawn_moves

    def generate_black_pawn_attacks(self, pawn_square, occupancy_white):
        pawn_attacks = []
        if np.bitwise_and(self.piece_bitboards["black_pawn"], (np.uint64(1) << np.uint8(pawn_square))):
            move_bitboard = np.bitwise_and(PAWN_ATTACKS_BLACK[pawn_square], occupancy_white)
            for move_square in range(64):
                if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                    pawn_attacks.append(Move(start_square=pawn_square, end_square=move_square, move_type="BLACK PAWN ATTACK"))

        return pawn_attacks


    def generate_knight_moves(self):
        knight_moves = []

        for knight_square in range(64):
            knight_moves.extend(self.generate_single_knight_moves(knight_square))

        return knight_moves

    def generate_single_knight_moves(self, knight_square):
        knight_moves = []
        occupancy_white = np.uint64(0)
        occupancy_black = np.uint64(0)

        for piece_type, bitboard in self.piece_bitboards.items():
            if "white" in piece_type:
                occupancy_white = np.bitwise_or(occupancy_white, bitboard)
            else:
                occupancy_black = np.bitwise_or(occupancy_black, bitboard)

        if self.color == COLOR_WHITE:
            if np.bitwise_and(self.piece_bitboards["white_knight"], (np.uint64(1) << np.uint8(knight_square))):
                move_bitboard = np.bitwise_and(KNIGHT_MOVES[knight_square], np.bitwise_not(occupancy_white))
                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        knight_moves.append(Move(start_square=knight_square, end_square=move_square, move_type="WHITE KNIGHT MOVE"))
        else:
            if np.bitwise_and(self.piece_bitboards["black_knight"], (np.uint64(1) << np.uint8(knight_square))):
                move_bitboard = np.bitwise_and(KNIGHT_MOVES[knight_square], np.bitwise_not(occupancy_black))
                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        knight_moves.append(Move(start_square=knight_square, end_square=move_square, move_type="BLACK KNIGHT MOVE"))

        return knight_moves

    def generate_king_moves(self):
        king_moves = []

        for king_square in range(64):
            king_moves.extend(self.generate_single_king_moves(king_square))

        return king_moves

    def generate_single_king_moves(self, king_square):
        king_moves = []
        occupancy_white = np.uint64(0)
        occupancy_black = np.uint64(0)

        for piece_type, bitboard in self.piece_bitboards.items():
            if "white" in piece_type:
                occupancy_white = np.bitwise_or(occupancy_white, bitboard)
            else:
                occupancy_black = np.bitwise_or(occupancy_black, bitboard)

        if self.color == COLOR_WHITE:
            if np.bitwise_and(self.piece_bitboards["white_king"], (np.uint64(1) << np.uint8(king_square))):
                move_bitboard = np.bitwise_and(KING_MOVES[king_square], np.bitwise_not(occupancy_white))
                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        king_moves.append(Move(start_square=king_square, end_square=move_square, move_type="WHITE KING MOVE"))
        else:
            if np.bitwise_and(self.piece_bitboards["black_king"], (np.uint64(1) << np.uint8(king_square))):
                move_bitboard = np.bitwise_and(KING_MOVES[king_square], np.bitwise_not(occupancy_black))
                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        king_moves.append(Move(start_square=king_square, end_square=move_square, move_type="BLACK KING MOVE"))

        return king_moves


    def generate_rook_moves(self):
        rook_moves = []

        for rook_square in range(64):
            rook_moves.extend(self.generate_single_rook_moves(rook_square))

        return rook_moves

    def generate_single_rook_moves(self, rook_square):
        rook_moves = []
        occupancy_white = np.uint64(0)
        occupancy_black = np.uint64(0)

        for piece_type, bitboard in self.piece_bitboards.items():
            if "white" in piece_type:
                occupancy_white = np.bitwise_or(occupancy_white, bitboard)
            else:
                occupancy_black = np.bitwise_or(occupancy_black, bitboard)

        occupancy = np.bitwise_or(occupancy_white, occupancy_black)

        occupancy = np.bitwise_and(occupancy, ROOK_MASKS[rook_square])
        occupancy = occupancy * ROOK_MAGIC_NUMBERS[rook_square]
        occupancy = occupancy >> np.uint8(64 - ROOK_MAGIC_SHIFTS[rook_square])

        move_bitboard = ROOK_MOVES[rook_square][occupancy]
        # if bishop_square == 35:
        #     print("OCCUPANCY: ", occupancy)
        #     print_bitboard(move_bitboard)
        #self.print_bitboard(move_bitboard)

        if self.color == COLOR_WHITE:
            if np.bitwise_and(self.piece_bitboards["white_rook"], (np.uint64(1) << np.uint8(rook_square))):
                move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(occupancy_white))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        rook_moves.append(Move(start_square=rook_square, end_square=move_square, move_type="WHITE ROOK MOVE"))
        else:
            if np.bitwise_and(self.piece_bitboards["black_rook"], (np.uint64(1) << np.uint8(rook_square))):
                move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(occupancy_black))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        rook_moves.append(Move(start_square=rook_square, end_square=move_square, move_type="BLACK ROOK MOVE"))

        return rook_moves


    def generate_bishop_moves(self):
        bishop_moves = []

        for bishop_square in range(64):
            bishop_moves.extend(self.generate_single_bishop_moves(bishop_square))

        return bishop_moves

    def generate_single_bishop_moves(self, bishop_square):
        bishop_moves = []
        occupancy_white = np.uint64(0)
        occupancy_black = np.uint64(0)

        for piece_type, bitboard in self.piece_bitboards.items():
            if "white" in piece_type:
                occupancy_white = np.bitwise_or(occupancy_white, bitboard)
            else:
                occupancy_black = np.bitwise_or(occupancy_black, bitboard)

        occupancy = np.bitwise_or(occupancy_white, occupancy_black)

        occupancy = np.bitwise_and(occupancy, BISHOP_MASKS[bishop_square])
        occupancy = occupancy * BISHOP_MAGIC_NUMBERS[bishop_square]
        occupancy = occupancy >> np.uint8(64 - BISHOP_MAGIC_SHIFTS[bishop_square])

        move_bitboard = BISHOP_MOVES[bishop_square][occupancy]
        # if bishop_square == 35:
        #     print("OCCUPANCY: ", occupancy)
        #     print_bitboard(move_bitboard)
        #self.print_bitboard(move_bitboard)

        if self.color == COLOR_WHITE:
            if np.bitwise_and(self.piece_bitboards["white_bishop"], (np.uint64(1) << np.uint8(bishop_square))):
                move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(occupancy_white))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        bishop_moves.append(Move(start_square=bishop_square, end_square=move_square, move_type="WHITE BISHOP MOVE"))
        else:
            if np.bitwise_and(self.piece_bitboards["black_bishop"], (np.uint64(1) << np.uint8(bishop_square))):
                move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(occupancy_black))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        bishop_moves.append(Move(start_square=bishop_square, end_square=move_square, move_type="BLACK BISHOP MOVE"))

        return bishop_moves


    def generate_queen_moves(self):
        return []

    def check_pseudo_move(self, move):
        return True
    
    def make_move(self, move):
        mover_type = self.get_piece_on_square(move.start_square)
        defender_type = self.get_piece_on_square(move.end_square)

        self.piece_bitboards[mover_type] = unset_bitboard_bit(move.start_square, self.piece_bitboards[mover_type])
        if defender_type:
            self.piece_bitboards[defender_type] = unset_bitboard_bit(move.end_square, self.piece_bitboards[defender_type])
        self.piece_bitboards[mover_type] = set_bitboard_bit(move.end_square, self.piece_bitboards[mover_type])

    def get_piece_on_square(self, square):
        for piece_type, piece_bitboard in self.piece_bitboards.items():
            if np.bitwise_and(piece_bitboard, (np.uint64(1) << np.uint8(square))):
                return piece_type
        return None


if __name__ == '__main__':
    board = Game()

    board.pretty_print_board()
    # for piece_type, bitboard in board.piece_bitboards.items():
    #     print(piece_type)
    #     board.print_bitboard(bitboard)
    for i in range(4):
        moves = board.generate_moves()
        for move in moves:
            print(move)
        board.make_move(moves[-1])
        board.pretty_print_board()
