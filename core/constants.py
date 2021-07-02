import numpy as np

from utils.bitboard_operations import *

print("INTIALIZATION START!")

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

print("PAWNS DONE!")

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

print("KNIGHTS DONE!")

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

print("KINGS DONE!")

# Sliding Pieces

# Bishop
def mask_bishop_moves(square):
    move_bitboard = np.uint64(0)

    square_rank = int(square / 8)
    square_file = int(square % 8)

    # Direction (1, 1)
    rank = square_rank + 1
    file = square_file + 1
    while (rank <= 6 and file <= 6):
        move_bitboard = np.bitwise_or(move_bitboard, np.uint64(1) << np.uint8(8 * rank + file))
        rank += 1
        file += 1

    # Direction (-1, 1)
    rank = square_rank - 1
    file = square_file + 1
    while (rank >= 1 and file <= 6):
        move_bitboard = np.bitwise_or(move_bitboard, np.uint64(1) << np.uint8(8 * rank + file))
        rank -= 1
        file += 1

    # Direction (1, -1)
    rank = square_rank + 1
    file = square_file - 1
    while (rank <= 6 and file >= 1):
        move_bitboard = np.bitwise_or(move_bitboard, np.uint64(1) << np.uint8(8 * rank + file))
        rank += 1
        file -= 1

    # Direction (-1, -1)
    rank = square_rank - 1
    file = square_file - 1
    while (rank >= 1 and file >= 1):
        move_bitboard = np.bitwise_or(move_bitboard, np.uint64(1) << np.uint8(8 * rank + file))
        rank -= 1
        file -= 1

    return move_bitboard


def calculate_bishop_moves(square, block_bitboard):
    move_bitboard = np.uint64(0)

    square_rank = int(square / 8)
    square_file = int(square % 8)

    # Direction (1, 1)
    rank = square_rank + 1
    file = square_file + 1
    while (rank <= 7 and file <= 7):
        move_bitboard = np.bitwise_or(move_bitboard, np.uint64(1) << np.uint8(8 * rank + file))
        if np.bitwise_and(block_bitboard, np.uint64(1) << np.uint8(8 * rank + file)):
            break
        rank += 1
        file += 1

    # Direction (-1, 1)
    rank = square_rank - 1
    file = square_file + 1
    while (rank >= 0 and file <= 7):
        move_bitboard = np.bitwise_or(move_bitboard, np.uint64(1) << np.uint8(8 * rank + file))
        if np.bitwise_and(block_bitboard, np.uint64(1) << np.uint8(8 * rank + file)):
            break
        rank -= 1
        file += 1

    # Direction (1, -1)
    rank = square_rank + 1
    file = square_file - 1
    while (rank <= 7 and file >= 0):
        move_bitboard = np.bitwise_or(move_bitboard, np.uint64(1) << np.uint8(8 * rank + file))
        if np.bitwise_and(block_bitboard, np.uint64(1) << np.uint8(8 * rank + file)):
            break
        rank += 1
        file -= 1

    # Direction (-1, -1)
    rank = square_rank - 1
    file = square_file - 1
    while (rank >= 0 and file >= 0):
        move_bitboard = np.bitwise_or(move_bitboard, np.uint64(1) << np.uint8(8 * rank + file))
        if np.bitwise_and(block_bitboard, np.uint64(1) << np.uint8(8 * rank + file)):
            break
        rank -= 1
        file -= 1

    return move_bitboard


def set_occupancy(index, bits_in_mask, move_mask, square_temp):
    occupancy = np.uint64(0)
    for bit_count in range(bits_in_mask):
        square = get_ls1b_index(move_mask)
        move_mask = unset_bitboard_bit(square, move_mask)
        if np.bitwise_and(np.uint16(index), np.uint64(1) << np.uint8(bit_count)):
            occupancy = np.bitwise_or(occupancy, np.uint64(1) << np.uint8(square))

    return occupancy


# Slider Tables

# Magic Numbers and Shifts
# Bishop Magic Numbers
BISHOP_MAGIC_NUMBERS = np.array(
    [
        0x40040844404084,
        0x2004208a004208,
        0x10190041080202,
        0x108060845042010,
        0x581104180800210,
        0x2112080446200010,
        0x1080820820060210,
        0x3c0808410220200,
        0x4050404440404,
        0x21001420088,
        0x24d0080801082102,
        0x1020a0a020400,
        0x40308200402,
        0x4011002100800,
        0x401484104104005,
        0x801010402020200,
        0x400210c3880100,
        0x404022024108200,
        0x810018200204102,
        0x4002801a02003,
        0x85040820080400,
        0x810102c808880400,
        0xe900410884800,
        0x8002020480840102,
        0x220200865090201,
        0x2010100a02021202,
        0x152048408022401,
        0x20080002081110,
        0x4001001021004000,
        0x800040400a011002,
        0xe4004081011002,
        0x1c004001012080,
        0x8004200962a00220,
        0x8422100208500202,
        0x2000402200300c08,
        0x8646020080080080,
        0x80020a0200100808,
        0x2010004880111000,
        0x623000a080011400,
        0x42008c0340209202,
        0x209188240001000,
        0x400408a884001800,
        0x110400a6080400,
        0x1840060a44020800,
        0x90080104000041,
        0x201011000808101,
        0x1a2208080504f080,
        0x8012020600211212,
        0x500861011240000,
        0x180806108200800,
        0x4000020e01040044,
        0x300000261044000a,
        0x802241102020002,
        0x20906061210001,
        0x5a84841004010310,
        0x4010801011c04,
        0xa010109502200,
        0x4a02012000,
        0x500201010098b028,
        0x8040002811040900,
        0x28000010020204,
        0x6000020202d0240,
        0x8918844842082200,
        0x4010011029020020
    ],
    dtype = np.uint64
)
# Bishop Magic Shifts
BISHOP_MAGIC_SHIFTS = np.array(
    [
        6, 5, 5, 5, 5, 5, 5, 6, 
        5, 5, 5, 5, 5, 5, 5, 5, 
        5, 5, 7, 7, 7, 7, 5, 5, 
        5, 5, 7, 9, 9, 7, 5, 5, 
        5, 5, 7, 9, 9, 7, 5, 5, 
        5, 5, 7, 7, 7, 7, 5, 5, 
        5, 5, 5, 5, 5, 5, 5, 5, 
        6, 5, 5, 5, 5, 5, 5, 6
    ],
    dtype = np.uint8
)

# Bishop Tables
BISHOP_MASKS = np.zeros(64, dtype=np.uint64)
BISHOP_MOVES = np.zeros((64, 512), dtype=np.uint64)

# Rook Tables
ROOK_MASKS = np.zeros(64, dtype=np.uint64)
ROOK_MOVES = np.zeros((64, 4096), dtype=np.uint64)


# Init Slider Tables
def init_slider_tables(bishop):

    for square in range(64):
        BISHOP_MASKS[square] = mask_bishop_moves(square)
        # ROOK_MASKS[square] = mask_rook_moves(square)
        #print("SQUARE: ", square)
        if bishop:
            move_mask = BISHOP_MASKS[square]
        else:
            move_mask = ROOK_MASKS[square]

        relevant_bits_count = count_bitboard_bits(move_mask)

        occupancy_indicies = np.uint64(1) << np.uint8(relevant_bits_count)

        for index in range(occupancy_indicies):
            #print("INDEX: ", index)
            if bishop:
                #index = 9
                occupancy = set_occupancy(index, relevant_bits_count, move_mask, square)
                # print_bitboard(occupancy)
                # input()
                # file.write(str(index) + "\n")
                # ranks = [np.binary_repr(occupancy, 64)[y:y+8][::-1] for y in range(0, 64, 8)]
                # for rank in ranks:
                #     file.write(rank+"\n")
                # file.write("\n\n")

                magic_index = (occupancy * BISHOP_MAGIC_NUMBERS[square]) >> np.uint8(64 - BISHOP_MAGIC_SHIFTS[square])

                BISHOP_MOVES[square][magic_index] = calculate_bishop_moves(square, occupancy)
            
            # else:
            #     occupancy = set_occupancy(index, relevant_bits_count, move_mask)

            #     magic_index = (occupancy * ROOK_MAGIC_NUMBERS[square]) >> (64 - ROOK_MAGIC_SHIFTS[square])

            #     ROOK_MOVES[square][magic_index] = calculate_rook_moves(square, occupancy)
            

init_slider_tables(True)
# square = 0
# for i in BISHOP_MOVES:
#     with open(str(square) + ".txt", "w") as file:
#         index = 0
#         for x in i:
#             file.write(str(index) + "\n")
#             ranks = [np.binary_repr(x, 64)[y:y+8][::-1] for y in range(0, 64, 8)]
#             for rank in ranks:
#                 file.write(rank+"\n")
#             file.write("\n\n")
#             index += 1
#     square += 1


print("SLIDERS DONE!")
print("INTIALIZATION DONE!")

