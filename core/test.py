import numpy as np

chrs = {
    'b_pawn': u'\u265F',
    'b_rook': u'\u265C',
    'b_knight': u'\u265E',
    'b_bishop': u'\u265D',
    'b_king': u'\u265A',
    'b_queen': u'\u265B',

    'w_pawn': u'\u2659',
    'w_rook': u'\u2656',
    'w_knight': u'\u2658',
    'w_bishop': u'\u2657',
    'w_king': u'\u2654',
    'w_queen': u'\u2655'
}

#for item in chrs.values():
bitboard = np.uint64(20)
print(np.binary_repr(bitboard))
print(np.binary_repr(bitboard)[53])
print(np.binary_repr(bitboard)[2])