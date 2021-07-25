# gui and async

import pygame
import os
import numpy as np
from utils.bitboard_operations import unset_bitboard_bit, set_bitboard_bit, get_bitboard_bit, print_bitboard
from game import Game
import move
from humanPlayer import humanPlayer


def main():
    pygame.init()
    gui = GUI(800, 600)
    gui.load_pieces()
    # tracks which players turn --> 0 white and 1 black
    current_color = 0

    # instantiate human Players
    p_white = humanPlayer(gui.game.piece_bitboards, 0)
    p_black = humanPlayer(gui.game.piece_bitboards, 1)
    players = [p_white, p_black]

    # keeps track whether a turn is finished
    turn_finished = False

    selected_piece = None
    x_old = -1
    y_old = -1
    while True:
        gui.game_display.fill((255, 255, 255))
        piece, x, y = gui.draw_drag(selected_piece, x_old, y_old)
        # print(piece)
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # check if a piece was selected and if its the human player turn
                if piece != None and isinstance(players[current_color], humanPlayer):
                    # check if the selecting human player is allowed to move pieces of the selected color
                    if (current_color == 0 and "white" in piece) or (current_color == 1 and "black" in piece):
                        selected_piece, x_old, y_old = piece, x, y
                        print("X_old: " + str(x) + " Y_old:" + str(y))
                        # print(str(piece))
                    else:
                        piece = None
                else:
                    piece = None
            if event.type == pygame.MOUSEBUTTONUP:
                if piece != None and selected_piece != None:
                    print("Selected: " + selected_piece)
                    if piece == "":
                        print("Move to: " + "empty_field at: x=" +
                              str(x) + " y=" + str(y))
                    else:
                        print("Move to: " + piece + " at: x=" +
                              str(x) + " y=" + str(y))
                    # check if piece was not moved or empty field was selected
                    if selected_piece == "" or (x == x_old) and (y == y_old):
                        print("No Move")

                    # check move for validity in engine
                    # TODO: Send data here to engine and get new bitboards to draw
                    else:
                        # create a move
                        player_move = players[current_color].get_player_move(
                            x_old+y_old*8, x+y*8)

                        turn_finished, game_finished = gui.game.make_move(
                            player_move)
                        if game_finished:
                            print("FINISHED")
                        # # TODO: ENTFERNEN und durch ENGINE AKTUALISIERUNG ERSETZEN
                        # gui.game.piece_bitboards[selected_piece] = unset_bitboard_bit(
                        #     x_old+8*y_old, gui.game.piece_bitboards[selected_piece])

                        # gui.game.piece_bitboards[selected_piece] = set_bitboard_bit(
                        #     x+y*8, gui.game.piece_bitboards[selected_piece])

                        print("Moved")
                    print("X_new: " + str(x) + " Y_new: " + str(y))
                selected_piece = None
                x_old = -1
                y_old = -1

        if turn_finished:
            # change players turn when finished
            current_color = 1 if current_color == 0 else 0
            turn_finished = False

        gui.draw_pieces(gui.game.piece_bitboards)
        pygame.display.flip()
        gui.clock.tick(30)


class GUI(pygame.sprite.Sprite):
    def __init__(self, width, height):
        self.width = int(width)
        self.height = int(height)
        self.game_display = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.offset_left_right = 0.1*width
        self.offset_top_bottom = 0.1*height
        self.board_length = self.height-2*self.offset_top_bottom
        self.board = pygame.Surface((self.board_length, self.board_length))
        self.board_draw_x = self.width/2 - self.board_length/2
        self.board_draw_y = self.height/2 - self.board_length/2
        self.piece_length = int(self.board_length/8)
        self.pieces = self.load_pieces()
        self.game = Game()
        self.all_sprites = pygame.sprite.Group()

        # list for keeping all fields logically
        # a zero represents no unit on field
        self.current_board = np.zeros(64, dtype='U15')

    def get_square_under_mouse(self):
        x, y = pygame.Vector2(pygame.mouse.get_pos())
        x = (x-self.board_draw_x) / self.piece_length
        y = 8-(y-self.board_draw_y) / self.piece_length
        if x >= 0 and y >= 0 and x < 8 and y < 8:
            x = int(x)
            y = int(y)
            return (self.current_board[x+8*y], x, y)

        return None, None, None

    def draw_pieces(self, bitboards):
        # draw black and white fields
        # self.game_display.fill((255, 255, 255))
        self.game_display.blit(
            self.board, (self.board_draw_x, self.board_draw_y))

        # Draw board background
        for x in range(8):
            for y in range(8):
                if (x+y) % 2 == 0:
                    # print((x+y) % 2)
                    # draw black field
                    # brown
                    pygame.draw.rect(self.board, (125, 63, 59), (self.piece_length * x, self.piece_length *
                                     (7-y), self.piece_length, self.piece_length))
                else:
                    pygame.draw.rect(self.board, (194, 181, 180), (self.piece_length * x, self.piece_length *
                                     (7-y), self.piece_length, self.piece_length))
                    # draw board onto screen
        self.current_board = np.zeros(64, dtype='U15')

        for key, bitboard in bitboards.items():
            for i in range(64):
                x = 0
                y = 0
                tmp_bitboard = get_bitboard_bit(i, bitboard)
                # if key == "black_king":
                # print(key + " :" + str(tmp_bitboard))
                if tmp_bitboard != 0:
                    y = int(i / 8)
                    x = int(i % 8)
                    self.current_board[i] = key
                    self.pieces[key].x = self.piece_length * x
                    self.pieces[key].y = self.board_length - \
                        ((y+1)*self.piece_length)
                    self.board.blit(
                        self.pieces[key].image, (self.pieces[key].x, self.pieces[key].y))

                # print()

    def draw_drag(self, selected_piece, old_x, old_y, font=False):
        piece, x, y = self.get_square_under_mouse()
        if selected_piece:

            if x != None:
                rect = (x * self.piece_length,
                        (7-y) * self.piece_length, self.piece_length, self.piece_length)
                pygame.draw.rect(self.board, (0, 255, 0, 50), rect, 2)

            # color, type = selected_piece[0]
            # s1 = font.render(type[0], True, pygame.Color(color))
            # s2 = font.render(type[0], True, pygame.Color('darkgrey'))

                old_rect = (old_x * self.piece_length,
                            (7-old_y) * self.piece_length, self.piece_length, self.piece_length)
                pygame.draw.rect(
                    self.board, (255, 0, 0, 50), old_rect, 2)

                pygame.draw.line(self.board, pygame.Color(
                    'red'), (old_x * self.piece_length + self.piece_length/2,
                             (7-old_y) * self.piece_length + self.piece_length/2), (x * self.piece_length + self.piece_length/2,
                                                                                    (7-y) * self.piece_length + self.piece_length/2))
        return piece, x, y

    def load_pieces(self):
        # piece images from: https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces/Standard
        piece_files = [item for item in os.listdir("piece_images")]
        pieces = {}
        for piece_file in piece_files:
            piece = pygame.image.load(os.path.join(
                "piece_images", piece_file)).convert_alpha()
            piece = pygame.transform.scale(
                piece, (self.piece_length, self.piece_length))
            pieces[piece_file[:-4]] = piece_class((0, 0), piece)

        return pieces
        """
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
        """


class piece_class(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self.x, self.y = pos
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.msg = "HI"


if __name__ == "__main__":
    main()
