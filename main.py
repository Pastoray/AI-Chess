import pygame as pg
from constants import * 
from game import *
from image_loader import load_image_path
import sys

pg.init()
pg.mixer.init()

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")

logo = pg.image.load(LOGO_PATH)
pg.display.set_icon(logo)

clock = pg.time.Clock()

font = pg.font.Font(FONT_PATH, FONT_SIZE)
chessboard = ChessBoard(WHITE, TILE)

def draw_pieces():
    for i in range(len(chessboard.board)):
        for j in range(len(chessboard.board[i])):
            piece = chessboard.get_piece(j, i)
            if piece:
                x = j * TILE
                y = i * TILE
                image_path = load_image_path(piece.name(), piece.color)
                image = pg.image.load(image_path)
                screen.blit(image, (x, y))

def display_text(text, color):
    text = font.render(text, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

def determine_winner():
    if chessboard.get_winner() == WHITE:
        display_text("WHITE WON", GREEN)
    elif chessboard.get_winner() == BLACK:
        display_text("BLACK WON", RED)
    elif chessboard.get_winner() == None:
        display_text("DRAW WON", GRAY)
    pg.display.update()
    pg.time.delay(3000)
    chessboard.reset()

def promote_pawn(color):
    mouse_pos = pg.mouse.get_pos()
    x = mouse_pos[0] // TILE
    y = mouse_pos[1] // TILE
    if color == BLACK:
        x2, y2 = chessboard.black_pawn_promoted
        if x == x2 and y <= y2 <= y + 3:
            if y2 == y + 3:
                chessboard.board[y2][x2] = Knight(BLACK, chessboard)
                chessboard.black_pawn_promoted = None
                chessboard.play_sound((y2, x2))
            elif y2 == y + 2:
                chessboard.board[y2][x2] = Bishop(BLACK, chessboard)
                chessboard.black_pawn_promoted = None
                chessboard.play_sound((y2, x2))
            elif y2 == y + 1:
                chessboard.board[y2][x2] = Rook(BLACK, chessboard)
                chessboard.black_pawn_promoted = None
                chessboard.play_sound((y2, x2))
            elif y2 == y:
                chessboard.board[y2][x2] = Queen(BLACK, chessboard)
                chessboard.black_pawn_promoted = None
                chessboard.play_sound((y2, x2))
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            chessboard.valid_black_moves[(x2, y2)] = chessboard.get_piece(x2, y2).get_valid_moves((x2, y2))
            for x, y, p in chessboard.valid_black_moves[(x2, y2)]:
                chessboard.invalid_white_king_moves.append((x, y))
            x, y = chessboard.white_king
            chessboard.valid_white_moves[(x, y)] = chessboard.get_piece(x, y).get_valid_moves((x, y))
            for i in range(len(chessboard.board)):
                for j in range(len(chessboard.board[i])):
                    if chessboard.get_piece(j, i) and chessboard.get_piece(j, i).color == WHITE:
                        if chessboard.get_piece(j, i).name() != KING:
                            chessboard.valid_white_moves[(j, i)] = chessboard.valid_blocking_moves((i, j), WHITE)
                        else:
                            chessboard.valid_white_moves[(j, i)] = []
                            piece_movements = chessboard.get_piece(j, i).get_valid_moves((j, i))
                            for x, y, p in piece_movements:
                                if p != -1:
                                    chessboard.valid_white_moves[(j, i)].append((x, y, p))

            if len(max(chessboard.valid_black_moves.values(), key=len)) == 0:
                if chessboard.white_king not in chessboard.invalid_white_king_moves:
                    chessboard.winner = None
                else:
                    chessboard.winner = WHITE

    elif color == WHITE:
        x2, y2 = chessboard.white_pawn_promoted
        if x == x2 and y - 3 <= y2 <= y:
            if y2 == y - 3:
                chessboard.board[y2][x2] = Knight(WHITE, chessboard)
                chessboard.white_pawn_promoted = None
                chessboard.play_sound((y2, x2))
            elif y2 == y - 2:
                chessboard.board[y2][x2] = Bishop(WHITE, chessboard)
                chessboard.white_pawn_promoted = None
                chessboard.play_sound((y2, x2))
            elif y2 == y - 1:
                chessboard.board[y2][x2] = Rook(WHITE, chessboard)
                chessboard.white_pawn_promoted = None
                chessboard.play_sound((y2, x2))
            elif y2 == y:
                chessboard.board[y2][x2] = Queen(WHITE, chessboard)
                chessboard.white_pawn_promoted = None
                chessboard.play_sound((y2, x2))
            chessboard.valid_white_moves[(x2, y2)] = chessboard.get_piece(x2, y2).get_valid_moves((x2, y2))
            for x, y, p in chessboard.valid_white_moves[(x2, y2)]:
                chessboard.invalid_black_king_moves.append((x, y))
            x, y = chessboard.black_king
            chessboard.valid_black_moves[(x, y)] = chessboard.get_piece(x, y).get_valid_moves((x, y))
            for i in range(len(chessboard.board)):
                for j in range(len(chessboard.board[i])):
                    if chessboard.get_piece(j, i) and chessboard.get_piece(j, i).color == BLACK:
                        if chessboard.get_piece(j, i).name() != KING:
                            chessboard.valid_black_moves[(j, i)] = chessboard.valid_blocking_moves((i, j), BLACK)
                        else:
                            chessboard.valid_black_moves[(j, i)] = []
                            piece_movements = chessboard.get_piece(j, i).get_valid_moves((j, i))
                            for x, y, p in piece_movements:
                                if p != -1:
                                    chessboard.valid_black_moves[(j, i)].append((x, y, p))

            if len(max(chessboard.valid_black_moves.values(), key=len)) == 0:
                if chessboard.black_king not in chessboard.invalid_black_king_moves:
                    chessboard.winner = None
                else:
                    chessboard.winner = WHITE
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)


def draw_promotion_options(color):
    if color == WHITE:
        x, y = chessboard.white_pawn_promoted
        knight = pg.image.load(load_image_path(KNIGHT, WHITE))
        bishop = pg.image.load(load_image_path(BISHOP, WHITE))
        rook = pg.image.load(load_image_path(ROOK, WHITE))
        queen = pg.image.load(load_image_path(QUEEN, WHITE))

        pg.draw.rect(screen, GHOST, (x * TILE, y * TILE, TILE, TILE * 4))

        screen.blit(knight, (x * TILE, (y + 3) * TILE))
        screen.blit(bishop, (x * TILE, (y + 2) * TILE))
        screen.blit(rook, (x * TILE, (y + 1) * TILE))
        screen.blit(queen, (x * TILE, y * TILE))

        mouse_x, mouse_y = pg.mouse.get_pos()
        if x * TILE <= mouse_x <= (x + 1) * TILE and y * TILE <= mouse_y <= (y + 4) * TILE:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
        else:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

    elif color == BLACK:
            x, y = chessboard.black_pawn_promoted
            knight = pg.image.load(load_image_path(KNIGHT, BLACK))
            bishop = pg.image.load(load_image_path(BISHOP, BLACK))
            rook = pg.image.load(load_image_path(ROOK, BLACK))
            queen = pg.image.load(load_image_path(QUEEN, BLACK))

            pg.draw.rect(screen, LIGHTGRAY, (x * TILE, (y - 3) * TILE, TILE, TILE * 4))
            
            screen.blit(knight, (x * TILE, (y - 3) * TILE))
            screen.blit(bishop, (x * TILE, (y - 2) * TILE))
            screen.blit(rook, (x * TILE, (y - 1) * TILE))
            screen.blit(queen, (x * TILE, y * TILE))

            mouse_x, mouse_y = pg.mouse.get_pos()
            if x * TILE <= mouse_x <= (x + 1) * TILE and (y - 3) * TILE <= mouse_y <= (y + 1) * TILE:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            else:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

def main():
    selected_piece_pos = None
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pg.mouse.get_pos()
                    x = mouse_pos[0] // TILE
                    y = mouse_pos[1] // TILE
                    if chessboard.black_pawn_promoted:
                        promote_pawn(BLACK)

                    elif chessboard.white_pawn_promoted:
                       promote_pawn(WHITE)

                    else:
                        if selected_piece_pos:
                            new_pos = (x, y)
                            chessboard.move_piece(selected_piece_pos, new_pos)
                            selected_piece_pos = None
                        else:
                            if chessboard.get_piece(x, y) != None:
                                selected_piece_pos = (x, y)

        screen.fill(WHITE)
        tiles = chessboard.create()
        for tile in tiles:
            c, tup = tile
            pg.draw.rect(screen, c, tup)
        
        if selected_piece_pos:
            px, py = selected_piece_pos
            pg.draw.rect(screen, YELLOW, (px * TILE, py * TILE, TILE, TILE))
            for x, y, p in chessboard.get_piece(px, py).idk(selected_piece_pos):
                if p == 0:
                    pg.draw.circle(screen, GRAY, (x * TILE + 10 + 15, y * TILE + 10 + 15), 8)
                elif p == 1:
                    pg.draw.rect(screen, RED, (x * TILE, y * TILE, TILE, TILE))
                elif p == -1:
                    pass

        draw_pieces()

        if chessboard.white_pawn_promoted:
            draw_promotion_options(WHITE)

        if chessboard.black_pawn_promoted:
            draw_promotion_options(BLACK)

        if chessboard.get_winner() != False:
            determine_winner()

        pg.display.update()
        clock.tick(FPS)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
