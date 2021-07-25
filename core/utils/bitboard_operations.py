import numpy as np


def print_bitboard(bitboard):
    ranks = [np.binary_repr(bitboard, 64)[i:i+8][::-1]
             for i in range(0, 64, 8)]
    for rank in ranks:
        print(rank)
    print()


def set_bitboard_bit(index, bitboard):
    set_board = np.uint64(1) << np.uint8(index)
    bitboard = np.bitwise_or(bitboard, set_board)
    return bitboard


def unset_bitboard_bit(index, bitboard):
    set_board = np.uint64(1) << np.uint8(index)
    unset_board = np.bitwise_not(set_board)
    bitboard = np.bitwise_and(bitboard, unset_board)
    return bitboard


def get_bitboard_bit(index, bitboard):
    pos_board = np.uint64(1) << np.uint8(index)
    get_board = np.bitwise_and(bitboard, pos_board)
    return get_board


def count_bitboard_bits(bitboard):
    count = 0

    bitboard = np.uint64(bitboard)

    while bitboard:
        count += 1
        bitboard = np.bitwise_and(bitboard, np.uint64(bitboard - np.uint8(1)))

    return count


def get_ls1b_index(bitboard):
    if bitboard:
        index = count_bitboard_bits(np.bitwise_and(
            bitboard, -bitboard) - np.uint8(1))
        return index
    else:
        return -1


#move_mask = np.uint64(0x0040201008040200)
# move_mask = np.uint64(0x0040000000000000)
# neg_move_mask = -move_mask
# and_move_mask = np.bitwise_and(move_mask, neg_move_mask)
# minus1_move_mask = and_move_mask - np.uint8(1)
# count = count_bitboard_bits(minus1_move_mask)
# print_bitboard(move_mask)
# print_bitboard(neg_move_mask)
# print_bitboard(and_move_mask)
# print_bitboard(minus1_move_mask)
# print(count)
# index = get_ls1b_index(move_mask)
# print(index)
# for i in range(count_bitboard_bits(move_mask)):
#     print_bitboard(move_mask)
#     index = get_ls1b_index(move_mask)
#     print(index)
#     move_mask = unset_bitboard_bit(index, move_mask)
