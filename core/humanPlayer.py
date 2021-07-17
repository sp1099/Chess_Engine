import player
import move


class humanPlayer(player.player):
    def __init__(self, bitboards, color) -> None:
        super().__init__(bitboards, color)

    def update_bitboards(self, bitboards):
        pass

    def get_player_move(self, start_sqaure, end_square):
        generated_move = move.Move(start_sqaure, end_square)

        # return the generated move and the flag that shows turn finished
        return generated_move
