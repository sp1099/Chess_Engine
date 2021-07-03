# gui and async

import pygame
import os
import numpy as np
from utils.bitboard_operations import get_bitboard_bit
from game import Game


def main():
    pygame.init()
    gui = GUI(800, 600)
    gui.load_pieces()
    while True:
        gui.game_display.fill((255, 255, 255))
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gui.draw_board(gui.game.piece_bitboards)
        pygame.display.update()
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

        # TODO: Draw pieces
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

    def draw_board(self, bitboards):
        # draw black and white fields
        self.game_display.blit(
            self.board, (self.board_draw_x, self.board_draw_y))

        for key, bitboard in bitboards.items():
            for i in range(64):
                x = 0
                y = 0
                tmp_bitboard = get_bitboard_bit(i, bitboard)
                # if key == "black_king":
                #print(key + " :" + str(tmp_bitboard))
                if tmp_bitboard != 0:
                    y = int(i / 8)
                    x = int(i % 8)
                    self.board.blit(
                        self.pieces[key].image, (self.piece_length*x, self.board_length-((y+1)*self.piece_length)))
                # print()

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

        self.image = image
        self.rect = self.image.get_rect(topleft=pos)


if __name__ == "__main__":
    main()
