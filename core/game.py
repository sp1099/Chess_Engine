import numpy as np

from constants import *
from move import Move
from utils.bitboard_operations import *
import re

class Game():

    def __init__(self):
        self.game_finished = False
        self.color = COLOR_WHITE
        self.turn_counter = 0



        self.en_passant_target = np.uint64(0)
        # 1  2  4  8
        # wk wq bk bq
        self.castling_rights = np.uint8(15)

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

        self.pseudo_bitboards = self.piece_bitboards.copy()

        self.init_pieces()
        self.legal_moves = self.generate_moves()

    def init_pieces(self):
        self.piece_bitboards["white_rook"] = set_bitboard_bit(
            0, self.piece_bitboards["white_rook"])
        self.piece_bitboards["white_rook"] = set_bitboard_bit(
            7, self.piece_bitboards["white_rook"])
        self.piece_bitboards["white_knight"] = set_bitboard_bit(
            1, self.piece_bitboards["white_knight"])
        self.piece_bitboards["white_knight"] = set_bitboard_bit(
            6, self.piece_bitboards["white_knight"])
        self.piece_bitboards["white_bishop"] = set_bitboard_bit(
            2, self.piece_bitboards["white_bishop"])
        self.piece_bitboards["white_bishop"] = set_bitboard_bit(
            5, self.piece_bitboards["white_bishop"])
        self.piece_bitboards["white_queen"] = set_bitboard_bit(
            3, self.piece_bitboards["white_queen"])
        self.piece_bitboards["white_king"] = set_bitboard_bit(
            4, self.piece_bitboards["white_king"])

        self.piece_bitboards["black_rook"] = set_bitboard_bit(
            63, self.piece_bitboards["black_rook"])
        self.piece_bitboards["black_rook"] = set_bitboard_bit(
            56, self.piece_bitboards["black_rook"])
        self.piece_bitboards["black_knight"] = set_bitboard_bit(
            62, self.piece_bitboards["black_knight"])
        self.piece_bitboards["black_knight"] = set_bitboard_bit(
            57, self.piece_bitboards["black_knight"])
        self.piece_bitboards["black_bishop"] = set_bitboard_bit(
            61, self.piece_bitboards["black_bishop"])
        self.piece_bitboards["black_bishop"] = set_bitboard_bit(
            58, self.piece_bitboards["black_bishop"])
        self.piece_bitboards["black_queen"] = set_bitboard_bit(
            59, self.piece_bitboards["black_queen"])
        self.piece_bitboards["black_king"] = set_bitboard_bit(
            60, self.piece_bitboards["black_king"])

        for i in range(8, 16):
            self.piece_bitboards["white_pawn"] = set_bitboard_bit(
                i, self.piece_bitboards["white_pawn"])
            self.piece_bitboards["black_pawn"] = set_bitboard_bit(
                63 - i, self.piece_bitboards["black_pawn"])

        # DEBUG
        self.piece_bitboards["white_queen"] = set_bitboard_bit(
            35, self.piece_bitboards["white_queen"])

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
        # TODO: castling moves
        pseudo_legal_moves.extend(self.generate_castling_moves())

        # Make pseudo legal moves and test for king checks
        legal_moves = []
        #print("MOVES:", len(pseudo_legal_moves))
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
                pawn_moves.extend(self.generate_white_pawn_moves(
                    pawn_square, np.bitwise_or(occupancy_white, occupancy_black)))
                pawn_attacks.extend(self.generate_white_pawn_attacks(
                    pawn_square, occupancy_black))
        else:
            for pawn_square in range(64):
                pawn_moves.extend(self.generate_black_pawn_moves(
                    pawn_square, np.bitwise_or(occupancy_white, occupancy_black)))
                pawn_attacks.extend(self.generate_black_pawn_attacks(
                    pawn_square, occupancy_white))

        return (pawn_moves + pawn_attacks)

    def generate_white_pawn_moves(self, pawn_square, board_occupancy):
        pawn_moves = []
        if np.bitwise_and(self.piece_bitboards["white_pawn"], (np.uint64(1) << np.uint8(pawn_square))):
            move_bitboard = np.bitwise_and(
                PAWN_MOVES_WHITE[pawn_square], np.bitwise_not(board_occupancy))
            for move_square in range(64):
                if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                    pawn_moves.append(Move(
                        start_square=pawn_square, end_square=move_square, piece_type=PAWN))

        if len(pawn_moves) == 1:
            if abs(pawn_moves[0].start_square - pawn_moves[0].end_square) == 16:
                pawn_moves = []

        return pawn_moves

    def generate_white_pawn_attacks(self, pawn_square, occupancy_black):
        pawn_attacks = []
        if np.bitwise_and(self.piece_bitboards["white_pawn"], (np.uint64(1) << np.uint8(pawn_square))):
            move_bitboard = np.bitwise_and(
                PAWN_ATTACKS_WHITE[pawn_square], np.bitwise_or(occupancy_black, self.en_passant_target))
            for move_square in range(64):
                if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                    pawn_attacks.append(Move(
                        start_square=pawn_square, end_square=move_square, piece_type=PAWN))

        return pawn_attacks

    def generate_black_pawn_moves(self, pawn_square, board_occupancy):
        pawn_moves = []
        if np.bitwise_and(self.piece_bitboards["black_pawn"], (np.uint64(1) << np.uint8(pawn_square))):
            move_bitboard = np.bitwise_and(
                PAWN_MOVES_BLACK[pawn_square], np.bitwise_not(board_occupancy))
            for move_square in range(64):
                if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                    pawn_moves.append(Move(
                        start_square=pawn_square, end_square=move_square, piece_type=PAWN))

        if len(pawn_moves) == 1:
            if abs(pawn_moves[0].start_square - pawn_moves[0].end_square) == 16:
                pawn_moves = []

        return pawn_moves

    def generate_black_pawn_attacks(self, pawn_square, occupancy_white):
        pawn_attacks = []
        if np.bitwise_and(self.piece_bitboards["black_pawn"], (np.uint64(1) << np.uint8(pawn_square))):
            move_bitboard = np.bitwise_and(
                PAWN_ATTACKS_BLACK[pawn_square], np.bitwise_or(occupancy_white, self.en_passant_target))
            for move_square in range(64):
                if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                    pawn_attacks.append(Move(
                        start_square=pawn_square, end_square=move_square, piece_type=PAWN))

        return pawn_attacks

    def generate_knight_moves(self):
        knight_moves = []

        for knight_square in range(64):
            knight_moves.extend(
                self.generate_single_knight_moves(knight_square))

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
                move_bitboard = np.bitwise_and(
                    KNIGHT_MOVES[knight_square], np.bitwise_not(occupancy_white))
                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        knight_moves.append(Move(
                            start_square=knight_square, end_square=move_square, piece_type=KNIGHT))
        else:
            if np.bitwise_and(self.piece_bitboards["black_knight"], (np.uint64(1) << np.uint8(knight_square))):
                move_bitboard = np.bitwise_and(
                    KNIGHT_MOVES[knight_square], np.bitwise_not(occupancy_black))
                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        knight_moves.append(Move(
                            start_square=knight_square, end_square=move_square, piece_type=KNIGHT))

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
                move_bitboard = np.bitwise_and(
                    KING_MOVES[king_square], np.bitwise_not(occupancy_white))
                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        king_moves.append(Move(
                            start_square=king_square, end_square=move_square, piece_type=KING))
        else:
            if np.bitwise_and(self.piece_bitboards["black_king"], (np.uint64(1) << np.uint8(king_square))):
                move_bitboard = np.bitwise_and(
                    KING_MOVES[king_square], np.bitwise_not(occupancy_black))
                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        king_moves.append(Move(
                            start_square=king_square, end_square=move_square, piece_type=KING))

        return king_moves

    def generate_rook_moves(self):
        rook_moves = []

        for rook_square in range(64):
            rook_moves.extend(self.generate_single_rook_moves(rook_square))

        return rook_moves

    def generate_single_rook_moves(self, rook_square, get_bitboard=False):
        if get_bitboard:
            bitboards = self.pseudo_bitboards
        else:
            bitboards = self.piece_bitboards

        rook_moves = []
        occupancy_white = np.uint64(0)
        occupancy_black = np.uint64(0)

        for piece_type, bitboard in bitboards.items():
            if "white" in piece_type:
                occupancy_white = np.bitwise_or(occupancy_white, bitboard)
            else:
                occupancy_black = np.bitwise_or(occupancy_black, bitboard)

        occupancy = np.bitwise_or(occupancy_white, occupancy_black)

        occupancy = np.bitwise_and(occupancy, ROOK_MASKS[rook_square])
        occupancy = occupancy * ROOK_MAGIC_NUMBERS[rook_square]
        occupancy = occupancy >> np.uint8(64 - ROOK_MAGIC_SHIFTS[rook_square])

        move_bitboard = ROOK_MOVES[rook_square][occupancy]

        if self.color == COLOR_WHITE:
            if np.bitwise_and(bitboards["white_rook"], (np.uint64(1) << np.uint8(rook_square))):
                move_bitboard = np.bitwise_and(
                    move_bitboard, np.bitwise_not(occupancy_white))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        rook_moves.append(Move(
                            start_square=rook_square, end_square=move_square, piece_type=ROOK))
        else:
            if np.bitwise_and(bitboards["black_rook"], (np.uint64(1) << np.uint8(rook_square))):
                move_bitboard = np.bitwise_and(
                    move_bitboard, np.bitwise_not(occupancy_black))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        rook_moves.append(Move(
                            start_square=rook_square, end_square=move_square, piece_type=ROOK))

        if get_bitboard:
            return move_bitboard
        else:
            return rook_moves

    def generate_bishop_moves(self):
        bishop_moves = []

        for bishop_square in range(64):
            bishop_moves.extend(
                self.generate_single_bishop_moves(bishop_square))

        return bishop_moves

    def generate_single_bishop_moves(self, bishop_square, get_bitboard=False):
        if get_bitboard:
            bitboards = self.pseudo_bitboards
        else:
            bitboards = self.piece_bitboards

        bishop_moves = []
        occupancy_white = np.uint64(0)
        occupancy_black = np.uint64(0)

        for piece_type, bitboard in bitboards.items():
            if "white" in piece_type:
                occupancy_white = np.bitwise_or(occupancy_white, bitboard)
            else:
                occupancy_black = np.bitwise_or(occupancy_black, bitboard)

        occupancy = np.bitwise_or(occupancy_white, occupancy_black)

        occupancy = np.bitwise_and(occupancy, BISHOP_MASKS[bishop_square])
        occupancy = occupancy * BISHOP_MAGIC_NUMBERS[bishop_square]
        occupancy = occupancy >> np.uint8(
            64 - BISHOP_MAGIC_SHIFTS[bishop_square])

        move_bitboard = BISHOP_MOVES[bishop_square][occupancy]

        if self.color == COLOR_WHITE:
            if np.bitwise_and(bitboards["white_bishop"], (np.uint64(1) << np.uint8(bishop_square))):
                move_bitboard = np.bitwise_and(
                    move_bitboard, np.bitwise_not(occupancy_white))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        bishop_moves.append(Move(
                            start_square=bishop_square, end_square=move_square, piece_type=BISHOP))
        else:
            if np.bitwise_and(bitboards["black_bishop"], (np.uint64(1) << np.uint8(bishop_square))):
                move_bitboard = np.bitwise_and(
                    move_bitboard, np.bitwise_not(occupancy_black))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        bishop_moves.append(Move(
                            start_square=bishop_square, end_square=move_square, piece_type=BISHOP))

        if get_bitboard:
            return move_bitboard
        else:
            return bishop_moves

    def generate_queen_moves(self):
        queen_moves = []

        for queen_square in range(64):
            queen_moves.extend(self.generate_single_queen_moves(queen_square))

        return queen_moves

    def generate_single_queen_moves(self, queen_square, get_bitboard=False):
        if get_bitboard:
            bitboards = self.pseudo_bitboards
        else:
            bitboards = self.piece_bitboards

        queen_moves = []
        occupancy_white = np.uint64(0)
        occupancy_black = np.uint64(0)

        for piece_type, bitboard in bitboards.items():
            if "white" in piece_type:
                occupancy_white = np.bitwise_or(occupancy_white, bitboard)
            else:
                occupancy_black = np.bitwise_or(occupancy_black, bitboard)

        occupancy_bishop = np.bitwise_or(occupancy_white, occupancy_black)
        occupancy_rook = np.bitwise_or(occupancy_white, occupancy_black)

        occupancy_bishop = np.bitwise_and(
            occupancy_bishop, BISHOP_MASKS[queen_square])
        occupancy_bishop = occupancy_bishop * \
            BISHOP_MAGIC_NUMBERS[queen_square]
        occupancy_bishop = occupancy_bishop >> np.uint8(
            64 - BISHOP_MAGIC_SHIFTS[queen_square])
        move_bitboard_bishop = BISHOP_MOVES[queen_square][occupancy_bishop]

        occupancy_rook = np.bitwise_and(
            occupancy_rook, ROOK_MASKS[queen_square])
        occupancy_rook = occupancy_rook * ROOK_MAGIC_NUMBERS[queen_square]
        occupancy_rook = occupancy_rook >> np.uint8(
            64 - ROOK_MAGIC_SHIFTS[queen_square])
        move_bitboard_rook = ROOK_MOVES[queen_square][occupancy_rook]

        move_bitboard = np.bitwise_or(move_bitboard_bishop, move_bitboard_rook)

        if self.color == COLOR_WHITE:
            if np.bitwise_and(bitboards["white_queen"], (np.uint64(1) << np.uint8(queen_square))):
                move_bitboard = np.bitwise_and(
                    move_bitboard, np.bitwise_not(occupancy_white))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        queen_moves.append(Move(
                            start_square=queen_square, end_square=move_square, piece_type=QUEEN))
        else:
            if np.bitwise_and(bitboards["black_queen"], (np.uint64(1) << np.uint8(queen_square))):
                move_bitboard = np.bitwise_and(
                    move_bitboard, np.bitwise_not(occupancy_black))

                for move_square in range(64):
                    if np.bitwise_and(move_bitboard, (np.uint64(1) << np.uint8(move_square))):
                        queen_moves.append(Move(
                            start_square=queen_square, end_square=move_square, piece_type=QUEEN))
        if get_bitboard:
            return move_bitboard
        else:
            return queen_moves

    def generate_castling_moves(self):
        castling_moves = []
        # 1  2  4  8
        # wk wq bk bq

        # white side
        if self.color == COLOR_WHITE:
            # check king side castling rights
            if self.castling_rights % 2 == 1:
                # check that no piece is inbetween king and king side rook
                if not self.check_square_occupied(5) and not self.check_square_occupied(6):
                    # king(e1) and f1 are not allowd to be under attack
                    if not self.check_square_for_attacked(4, COLOR_BLACK) and not self.check_square_for_attacked(5, COLOR_BLACK):
                        castling_moves.append(
                            Move(start_square=4, end_square=6, piece_type="castle"))
            # check queen side castling rights
            if (self.castling_rights >> 1) % 2 == 1:
                # check that no piece is inbetween king and queen side rook
                if not self.check_square_occupied(3) and not self.check_square_occupied(2) and not self.check_square_occupied(1):
                    # king(e1) and d1 are not allowd to be under attack
                    if not self.check_square_for_attacked(4, COLOR_BLACK) and not self.check_square_for_attacked(3, COLOR_BLACK):
                        castling_moves.append(
                            Move(start_square=4, end_square=2, piece_type="castle"))
        # black side
        else:
            # check king side castling rights
            if (self.castling_rights >> 2) % 2 == 1:
                # check that no piece is inbetween king and king side rook
                if not self.check_square_occupied(61) and not self.check_square_occupied(62):
                    # king(e8) and f8 are not allowd to be under attack
                    if not self.check_square_for_attacked(60, COLOR_WHITE) and not self.check_square_for_attacked(61, COLOR_WHITE):
                        castling_moves.append(
                            Move(start_square=60, end_square=62, piece_type="castle"))
            # check queen side castling rights
            if (self.castling_rights >> 3) % 2 == 1:
                # check that no piece is inbetween king and queen side rook
                if not self.check_square_occupied(59) and not self.check_square_occupied(58) and not self.check_square_occupied(57):
                    # king(e8) and d8 are not allowd to be under attack
                    if not self.check_square_for_attacked(60, COLOR_WHITE) and not self.check_square_for_attacked(59, COLOR_WHITE):
                        castling_moves.append(
                            Move(start_square=60, end_square=58, piece_type="castle"))

        return castling_moves

    def check_pseudo_move(self, move):
        # get king position of current color

        self.pseudo_bitboards = self.piece_bitboards.copy()
        self.make_move(move, use_pseudo_bitboards=True)
        current_color_king_field = get_ls1b_index(
            self.pseudo_bitboards["white_king" if self.color == 0 else "black_king"])
        return not self.check_square_for_attacked(
            current_color_king_field, 1-self.color, use_pseudo_bitboards=True)

    def make_move(self, move, use_pseudo_bitboards=False):

        current_legal_moves = [move]
        if use_pseudo_bitboards:
            bitboards = self.pseudo_bitboards
        else:
            bitboards = self.piece_bitboards
            current_legal_moves = self.legal_moves
            print(current_legal_moves)

            #print("Current legal moves: ", current_legal_moves)

        mover_type = self.get_piece_on_square(move.start_square)
        defender_type = self.get_piece_on_square(move.end_square)

        evaluation = [True for legal_move in current_legal_moves if (move.start_square ==
                                                                     legal_move.start_square and move.end_square ==
                                                                     legal_move.end_square)]

        if evaluation:
            if not use_pseudo_bitboards:
                print("Valid Move")

            # Unset mover_bitboard at start pos
            bitboards[mover_type] = unset_bitboard_bit(
                move.start_square, bitboards[mover_type])
            # Unset mover_bitboard at end pos

            # handle promotion
            if move.promotion_piece is not None:
                bitboards[move.promotion_piece] = set_bitboard_bit(
                    move.end_square, bitboards[move.promotion_piece])
            else:
                bitboards[mover_type] = set_bitboard_bit(
                    move.end_square, bitboards[mover_type])

            # Check for castling move
            if ("king" in mover_type):
                # white color
                if self.color == COLOR_WHITE:
                    # king side castling
                    if move.end_square == 6:
                        # Unset and set rook bitboards for castling
                        bitboards["white_rook"] = unset_bitboard_bit(
                            7, bitboards["white_rook"])
                        bitboards["white_rook"] = set_bitboard_bit(
                            5, bitboards["white_rook"])
                    # queen side castling
                    elif move.end_square == 2:
                        # Unset and set rook bitboards for castling
                        bitboards["white_rook"] = unset_bitboard_bit(
                            0, bitboards["white_rook"])
                        bitboards["white_rook"] = set_bitboard_bit(
                            3, bitboards["white_rook"])
                # black color
                else:
                    # king side castling
                    if move.end_square == 62:
                        # Unset and set rook bitboards for castling
                        bitboards["black_rook"] = unset_bitboard_bit(
                            63, bitboards["black_rook"])
                        bitboards["black_rook"] = set_bitboard_bit(
                            61, bitboards["black_rook"])
                    # queen side castling
                    elif move.end_square == 58:
                        # Unset and set rook bitboards for castling
                        bitboards["black_rook"] = unset_bitboard_bit(
                            56, bitboards["black_rook"])
                        bitboards["black_rook"] = set_bitboard_bit(
                            59, bitboards["black_rook"])

            # Check for en passant target
            if ("pawn" in mover_type) and (move.end_square == get_ls1b_index(self.en_passant_target)):
                if self.color == 0:
                    en_passant_defender = move.end_square - 8
                else:
                    en_passant_defender = move.end_square + 8
                defender_type = self.get_piece_on_square(en_passant_defender)
                # Unset defender_bitboard at end pos
                bitboards[defender_type] = unset_bitboard_bit(
                    en_passant_defender, bitboards[defender_type])
            else:
                if defender_type:
                    bitboards[defender_type] = unset_bitboard_bit(
                        move.end_square, bitboards[defender_type])

            # Check for Rook or king movement and update castling rights
            # 1  2  4  8
            # wk wq bk bq
            if not use_pseudo_bitboards:
                if "rook" in mover_type and self.castling_rights != 0:
                    if np.bitwise_and(self.castling_rights, np.uint8(2)) and move.start_square == 0:
                        self.castling_rights = np.bitwise_and(
                            self.castling_rights, np.bitwise_not(np.uint8(2)))
                    elif np.bitwise_and(self.castling_rights, np.uint8(1)) and move.start_square == 7:
                        self.castling_rights = np.bitwise_and(
                            self.castling_rights, np.bitwise_not(np.uint8(1)))
                    elif np.bitwise_and(self.castling_rights, np.uint8(8)) and move.start_square == 56:
                        self.castling_rights = np.bitwise_and(
                            self.castling_rights, np.bitwise_not(np.uint8(8)))
                    elif np.bitwise_and(self.castling_rights, np.uint8(4)) and move.start_square == 63:
                        self.castling_rights = np.bitwise_and(
                            self.castling_rights, np.bitwise_not(np.uint8(4)))
                if "king" in mover_type and self.castling_rights != 0:
                    if np.bitwise_and(self.castling_rights, np.uint8(3)) and self.color == 0:
                        self.castling_rights = np.bitwise_and(
                            self.castling_rights, np.bitwise_not(np.uint8(3)))
                    elif np.bitwise_and(self.castling_rights, np.uint8(12)) and self.color == 1:
                        self.castling_rights = np.bitwise_and(
                            self.castling_rights, np.bitwise_not(np.uint8(12)))

                print("CASTLING RIGHTS: ", self.castling_rights)

                # Set or unset en passant target sqaure
                self.en_passant_target = np.uint64(0)
                if "pawn" in mover_type:
                    if abs(move.end_square - move.start_square) == 16:
                        self.en_passant_target = np.uint64(1) << np.uint8(
                            (move.start_square + move.end_square) / 2)

                # swap color if method called for actual movement (not pseudo)
            if not use_pseudo_bitboards:
                self.color = 1-self.color
                self.legal_moves = self.generate_moves()
                # check if checkmate
                self.game_finished = True if not self.legal_moves else False

            return True, self.game_finished
        else:
            print("Not a valid move")
            # turn_finished, game_finished
            return False, self.game_finished

    def get_piece_on_square(self, square):
        for piece_type, piece_bitboard in self.piece_bitboards.items():
            if np.bitwise_and(piece_bitboard, (np.uint64(1) << np.uint8(square))):
                return piece_type
        return None

    def check_square_for_attacked(self, square, color, use_pseudo_bitboards=False):
        """check square for attacked by given color

        Args:
            square ([type]): [square field watched]
            color ([type]): [attacking color]
        """

        if use_pseudo_bitboards:
            bitboards = self.pseudo_bitboards
        else:
            bitboards = self.piece_bitboards

        # check if square attack by white pawn
        if (color == COLOR_WHITE and np.bitwise_and(PAWN_ATTACKS_BLACK[square], bitboards["white_pawn"])):
            return True
        # check if square attack by black pawn
        if (color == COLOR_BLACK and np.bitwise_and(PAWN_ATTACKS_WHITE[square], bitboards["black_pawn"])):
            return True

        # check if square attack by white knight
        if (color == COLOR_WHITE and np.bitwise_and(KNIGHT_MOVES[square], bitboards["white_knight"])):
            return True
        # check if square attack by black knight
        if (color == COLOR_BLACK and np.bitwise_and(KNIGHT_MOVES[square], bitboards["black_knight"])):
            return True

        # check if square attack by white king
        if (color == COLOR_WHITE and np.bitwise_and(KING_MOVES[square], bitboards["white_king"])):
            return True
        # check if square attack by black king
        if (color == COLOR_BLACK and np.bitwise_and(KING_MOVES[square], bitboards["black_king"])):
            return True

        # check if square attack by white rook
        if (color == COLOR_WHITE and np.bitwise_and(self.generate_single_rook_moves(square, get_bitboard=True), bitboards["white_rook"])):
            return True
        # check if square attack by black rook
        if (color == COLOR_BLACK and np.bitwise_and(self.generate_single_rook_moves(square, get_bitboard=True), bitboards["black_rook"])):
            return True

        # check if square attack by white bishop
        if (color == COLOR_WHITE and np.bitwise_and(self.generate_single_bishop_moves(square, get_bitboard=True), bitboards["white_bishop"])):
            return True
        # check if square attack by black bishop
        if (color == COLOR_BLACK and np.bitwise_and(self.generate_single_bishop_moves(square, get_bitboard=True), bitboards["black_bishop"])):
            return True

        # check if square attack by white queen
        if (color == COLOR_WHITE and np.bitwise_and(self.generate_single_queen_moves(square, get_bitboard=True), bitboards["white_queen"])):
            return True
        # check if square attack by black queen
        if (color == COLOR_BLACK and np.bitwise_and(self.generate_single_queen_moves(square, get_bitboard=True), bitboards["black_queen"])):
            return True

        return False

    def check_square_occupied(self, square):
        board_occupancy = np.uint64(0)
        for bitboard in self.piece_bitboards.values():
            board_occupancy = np.bitwise_or(board_occupancy, bitboard)

        if get_bitboard_bit(square, board_occupancy):
            return True
        return False

    def forsyth_to_bitboards(self, forsyth_str: str) -> None:
        
        forsyth_parts = re.findall("([^\s]+)", forsyth_str)
        board_rows = re.findall("([^\/]+)", forsyth_parts[0])
        
        white_pawn = []
        white_knight = []
        white_bishop = []
        white_rook = []
        white_queen = []
        white_king = []
        black_pawn = []
        black_knight = []
        black_bishop = []
        black_rook = []
        black_queen = []
        black_king = []

        units = {  
                "white_pawn": white_pawn, 
                "white_knight": white_knight, 
                "white_bishop": white_bishop,
                "white_rook": white_rook,
                "white_queen": white_queen,
                "white_king": white_king,
                "black_pawn": black_pawn,
                "black_knight": black_knight,
                "black_bishop": black_bishop,
                "black_rook": black_rook,
                "black_queen": black_queen,
                "black_king": black_king                
                }


        # find all occurences of respective units and add them to their respective position lists
        for row_index, row_string in enumerate(board_rows):
            # reverse given row index as the string rows start from top to bottom
            # and numbering of fields in backend start from bottom to top
            row_index = (7 - row_index)*8

            offset = 0
            for i, unit in enumerate(row_string):
                if i != 0 and row_string[i-1].isdigit():
                    offset += int(row_string[i-1])-1
                
                if "p" in unit:
                    black_pawn.append(row_index + offset)
                elif "n" in unit:
                    black_knight.append(row_index + offset)
                elif "b" in unit:
                    black_bishop.append(row_index + offset)
                elif "r" in unit:
                    black_rook.append(row_index + offset)
                elif "q" in unit:
                    black_queen.append(row_index + offset)
                elif "k" in unit:
                    black_king.append(row_index + offset)

                elif "P" in unit:
                    white_pawn.append(row_index + offset)
                elif "N" in unit:
                    white_knight.append(row_index + offset)
                elif "B" in unit:
                    white_bishop.append(row_index + offset)
                elif "R" in unit:
                    white_rook.append(row_index + offset)
                elif "Q" in unit:
                    white_queen.append(row_index + offset)
                elif "K" in unit:
                    white_king.append(row_index + offset)


                offset += 1
        # clear current bitboards
        for key, bitboard in self.piece_bitboards.items():
            self.piece_bitboards[key] = np.uint64(0)
        # update bitboards with found positions
        for key, positions in units.items():
            for pos in positions:
                self.piece_bitboards[key] = set_bitboard_bit(pos, self.piece_bitboards[key])
        
        # set current color
        self.color = 0 if "w" in forsyth_parts[1] else 1

        # set castling rights
        # 1  2  4  8
        # wk wq bk bq
        castling_rights = 0
        castling_rights += 1 if "K" in forsyth_parts[2] else 0
        castling_rights += 2 if "Q" in forsyth_parts[2] else 0
        castling_rights += 4 if "k" in forsyth_parts[2] else 0
        castling_rights += 8 if "q" in forsyth_parts[2] else 0
        self.castling_rights = np.uint8(castling_rights)

        # set en passant target
        #test = self.char_number_to_64_board("A8")
        if "-" not in forsyth_parts[3]:
            
            en_passant_target = self.char_number_to_64_board(forsyth_parts[3])
            self.en_passant_target = np.uint64(en_passant_target) if en_passant_target is not None else np.uint64(0)
        else:
            self.en_passant_target = np.uint64(0)
        
        
        # set game_over_turn_counter
        self.game_over_turn_counter = int(forsyth_parts[4])
        
        # set current turn number
        self.turn_counter = int(forsyth_parts[5])
        
        pass

    def bitboards_to_forsyth(self) -> str:
        forsyth_str = ""
        forsyth_rows = {
            0: [],
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
        }

        unit_string_mapping = {
                "white_pawn": "P", 
                "white_knight": "N", 
                "white_bishop": "B",
                "white_rook": "R",
                "white_queen": "Q",
                "white_king": "K",
                "black_pawn": "p",
                "black_knight": "n",
                "black_bishop": "b",
                "black_rook": "r",
                "black_queen": "q",
                "black_king": "k"  
        }
        for unit, bitboard in self.piece_bitboards.items():
            positions = self.get_all_pos_in_bitboard(bitboard)
            for pos in positions:
                row_index = 7 - int(pos/8)
                column_index = pos%8
                forsyth_rows[row_index].append([unit, column_index])
        e=1
        for row, values  in forsyth_rows.items():
            if len(values) != 0:
                # sort all units ascending depending on position
                values.sort(key=lambda x: x[1])
                # add blank field numbers to string
                row_string = ""
                offset = 0
                for i, unit in enumerate(values):
                    field_index = unit[1]
                    if i == 0:
                        if unit[1] == 0:
                            row_string += unit_string_mapping[unit[0]]
                            offset += 1
                        else:
                            row_string += str(unit[1])
                            row_string += unit_string_mapping[unit[0]]
                            offset += int(unit[1])
                    else:
                        tmp_offset = field_index - values[i-1][1]
                        if tmp_offset == 1:
                            row_string += unit_string_mapping[unit[0]]
                            offset += 1
                        else:
                            row_string += str(tmp_offset-1)+unit_string_mapping[unit[0]]
                            offset += tmp_offset
                        
                        if unit[0].isdigit():
                            offset += tmp_offset

                offset = 7 - offset
                if offset > 0:
                    row_string += str(offset)
                forsyth_str += row_string
            else:
                forsyth_str += "8"
            
            if row < 7:
                forsyth_str += "/"
            else:
                forsyth_str += " "
            
        # set players turn
        forsyth_str += "w " if self.color == 0 else "b "  

        # set castling rights
        # 1  2  4  8
        # wk wq bk bq
        forsyth_str += "K" if (self.castling_rights % 2) == 1 else ""
        forsyth_str += "Q" if (self.castling_rights >> 1) % 2 == 1 else ""
        forsyth_str += "k" if (self.castling_rights >> 2) % 2 == 1 else ""
        forsyth_str += "q" if (self.castling_rights >> 3) % 2 == 1 else ""

        if forsyth_str[-1] == " ":
            forsyth_str += "-"
        
        forsyth_str += " "

        if self.en_passant_target == np.uint64(0):
            forsyth_str += "-"
        else:
            en_passant = self.board_64_to_char_number(self.en_passant_target)
            forsyth_str += str(en_passant)

        forsyth_str += " "

        forsyth_str += str(self.game_over_turn_counter)

        forsyth_str += " "

        forsyth_str += str(self.turn_counter)


        return forsyth_str

    def get_all_pos_in_bitboard(self, bitboard):
        tmp_bitboard = bitboard.copy()
        positions = []
    
        while True:
            # find all bit positions in bitboard
            index = get_ls1b_index(tmp_bitboard)
            if index != -1:
                tmp_bitboard = unset_bitboard_bit(index, tmp_bitboard)
                positions.append(index)
            else: 
                break

        return positions

    def char_number_to_64_board(self, char_number:str):
        # calcuate position in 64 bitboard from e.g a3 (<-- = 16)
        row = int(char_number[-1])
        
        char = char_number[0]
        char_int = ord(char) - 97
        if row < 1 or row > 8 or char_int < 0 or char_int > 7:
            return None
        else:
            return (row-1)*8 + char_int

    def board_64_to_char_number(self, board_64:int):
        row = int(board_64 / 8) + 1
        column = int(board_64 % 8)

        char_column = chr(column + 97)
        return char_column + str(row)




if __name__ == '__main__':
    board = Game()

    board.forsyth_to_bitboards("4k2r/pb3pp1/1p2n2p/8/3P4/1PQ2B2/P4PPP/3RK2R w Kk - 0 1")
    forsyth_str = board.bitboards_to_forsyth()
    print(forsyth_str)
    board.pretty_print_board()
    # for piece_type, bitboard in board.piece_bitboards.items():
    #     print(piece_type)
    #     board.print_bitboard(bitboard)
    # for i in range(4):
    #     moves = board.generate_moves()
    #     for move in moves:
    #         print(move)
    #     board.make_move(moves[-1])
    #     board.pretty_print_board()
