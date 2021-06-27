import numpy as np

SQUARE_TABLE = [
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"
]

PIECE_UNICODE = {
    "black_pawn": u'\u2659',
    "black_knight": u'\u2658',
    "black_bishop": u'\u2657',
    "black_rook": u'\u2656',
    "black_queen": u'\u2655',
    "black_king": u'\u2654',

    "white_pawn": u'\u265F',
    "white_knight": u'\u265E',
    "white_bishop": u'\u265D',
    "white_rook": u'\u265C',
    "white_queen": u'\u265B',
    "white_king": u'\u265A'
}

COLOR_WHITE = 0
COLOR_BLACK = 1

PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6


def compute_white_pawn_moves(square):
    if square < 56:
        pos_bitboard = np.uint64(1) << np.uint8(square)
        move_bitboard = pos_bitboard << np.uint8(8)
        if 8 <= square <= 15:
            move_2_bitboard = pos_bitboard << np.uint8(16)
            move_bitboard = np.bitwise_or(move_bitboard, move_2_bitboard)
    else:
        move_bitboard = np.uint64(0)

    return move_bitboard

PAWN_MOVES_WHITE = np.fromiter(
    (compute_white_pawn_moves(square) for square in range(64)),
    dtype=np.uint64,
    count=64
)

def compute_white_pawn_attacks(square):
    if square < 56:
        pos_bitboard = np.uint64(1) << np.uint8(square)
        left_attack = pos_bitboard << np.uint8(7)
        right_attack = pos_bitboard << np.uint8(9)
        if square % 8 == 0:
            left_attack = np.uint64(0)
        elif square % 8 == 7:
            right_attack = np.uint64(0)
        move_bitboard = np.bitwise_or(left_attack, right_attack)
    else:
        move_bitboard = np.uint64(0)

    return move_bitboard

PAWN_ATTACKS_WHITE = np.fromiter(
    (compute_white_pawn_attacks(square) for square in range(64)),
    dtype=np.uint64,
    count=64
)


def compute_black_pawn_moves(square):
    if square > 7:
        pos_bitboard = np.uint64(1) << np.uint8(square)
        move_bitboard = pos_bitboard >> np.uint8(8)
        if 48 <= square <= 55:
            move_2_bitboard = pos_bitboard >> np.uint8(16)
            move_bitboard = np.bitwise_or(move_bitboard, move_2_bitboard)
    else:
        move_bitboard = np.uint64(0)

    return move_bitboard

PAWN_MOVES_BLACK = np.fromiter(
    (compute_black_pawn_moves(square) for square in range(64)),
    dtype=np.uint64,
    count=64
)

def compute_black_pawn_attacks(square):
    if square > 7:
        pos_bitboard = np.uint64(1) << np.uint8(square)
        left_attack = pos_bitboard >> np.uint8(7)
        right_attack = pos_bitboard >> np.uint8(9)
        if square % 8 == 0:
            right_attack = np.uint64(0)
        elif square % 8 == 7:
            left_attack = np.uint64(0)
        move_bitboard = np.bitwise_or(left_attack, right_attack)
    else:
        move_bitboard = np.uint64(0)

    return move_bitboard

PAWN_ATTACKS_BLACK = np.fromiter(
    (compute_black_pawn_attacks(square) for square in range(64)),
    dtype=np.uint64,
    count=64
)

def compute_knight_moves(square):
    pos_bitboard = np.uint64(1) << np.uint8(square)

    move_bitboard = np.uint64(0)
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard << np.uint8(10))) # 1 up, 2 left
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard << np.uint8(17))) # 2 up, 1 left
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard << np.uint8(15))) # 2 up, 1 right
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard << np.uint8(6))) # 1 up, 2 right
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard >> np.uint8(6))) # 1 down, 2 right
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard >> np.uint8(15))) # 2 down, 1 right
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard >> np.uint8(17))) # 2 down, 1 left
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard >> np.uint8(10))) # 1 down, 2 left

    if square % 8 in [0, 1]:
        move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(np.uint64(0xC0C0C0C0C0C0C0C0)))
    elif square % 8 in [6, 7]:
        move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(np.uint64(0x0303030303030303)))
    if square <= 15:
        move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(np.uint64(0xFFFF000000000000)))
    elif square >= 48:
        move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(np.uint64(0x000000000000FFFF)))

    return move_bitboard

KNIGHT_MOVES = np.fromiter(
    (compute_knight_moves(square) for square in range(64)),
    dtype=np.uint64,
    count=64
)

def compute_king_moves(square):
    pos_bitboard = np.uint64(1) << np.uint8(square)

    move_bitboard = np.uint64(0)
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard << np.uint8(1)))
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard << np.uint8(7)))
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard << np.uint8(8)))
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard << np.uint8(9)))
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard >> np.uint8(1)))
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard >> np.uint8(7)))
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard >> np.uint8(8)))
    move_bitboard = np.bitwise_or(move_bitboard, (pos_bitboard >> np.uint8(9)))

    if square % 8 == 0:
        move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(np.uint64(0x8080808080808080)))
    elif square % 8 == 7:
        move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(np.uint64(0x0101010101010101)))
    if square <= 7:
        move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(np.uint64(0xFF00000000000000)))
    elif square >= 56:
        move_bitboard = np.bitwise_and(move_bitboard, np.bitwise_not(np.uint64(0x00000000000000FF)))

    return move_bitboard

KING_MOVES = np.fromiter(
    (compute_king_moves(square) for square in range(64)),
    dtype=np.uint64,
    count=64
)