import pygame as pg
from constants import * 
from game import *
from image_loader import load_image_path
from ai import train, save, load
import sys
from logger import logger

pg.init()
pg.mixer.init()

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")

logo = pg.image.load(LOGO_PATH)
pg.display.set_icon(logo)

clock = pg.time.Clock()

font = pg.font.Font(FONT_PATH, FONT_SIZE)
chessboard = ChessBoard(WHITE, TILE)
selected_piece_pos = None
change = True

load()

def determine_winner(color):
    reward = 0
    if color == WHITE:
        reward = -1
        display_text("WHITE WON", GREEN)
        logger.info("White won!")
    elif color == BLACK:
        reward = 1
        display_text("BLACK WON", RED)
        logger.info("Black won!")
    elif color == None:
        display_text("DRAW", GRAY)
        logger.info("Draw!")
    train(chessboard.get_formated_board(), reward)
    pg.display.update()
    pg.time.delay(3000)
    chessboard.reset()

def draw_promotion_options(pos):
    x, y = pos
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

promotion_in_progress = False
promotion_pos = None
promotion_color = None
def promote_pawn(color, pos):
    global change, promotion_in_progress, promotion_pos, promotion_color
    change = True
    if color == WHITE:
        promotion_in_progress = True
        promotion_pos = pos
        promotion_color = color

def handle_promotion(x, y, color):
    global change, promotion_in_progress, promotion_pos, promotion_color
    mouse_pos = pg.mouse.get_pos()
    x2 = mouse_pos[0] // TILE
    y2 = mouse_pos[1] // TILE
    if color == BLACK and x == x2 and y <= y2 <= y - 3:
        if y2 == y - 3:
            chessboard.board[y][x] = Knight(BLACK, chessboard)
            chessboard.play_sound((y, x))
        elif y2 == y - 2:
            chessboard.board[y][x] = Bishop(BLACK, chessboard)
            chessboard.play_sound((y, x))
        elif y2 == y - 1:
            chessboard.board[y][x] = Rook(BLACK, chessboard)
            chessboard.play_sound((y, x))
        elif y2 == y:
            chessboard.board[y][x] = Queen(BLACK, chessboard)
            chessboard.play_sound((y, x))
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        chessboard.valid_black_moves[(x, y)] = chessboard.at(x, y).get_valid_moves((x, y))
        for x, y, _ in chessboard.valid_black_moves[(x, y)]:
            chessboard.invalid_white_king_moves.append((x, y))
        x, y = chessboard.white_king
        chessboard.valid_white_moves[(x, y)] = chessboard.at(x, y).get_valid_moves((x, y))
        chessboard.calculate_valid_moves(WHITE)

    elif color == WHITE and x == x2 and y <= y2 <= y + 3:
        if y2 == y + 3:
            chessboard.board[y][x] = Knight(WHITE, chessboard)
            chessboard.play_sound((y, x))
        elif y2 == y + 2:
            chessboard.board[y][x] = Bishop(WHITE, chessboard)
            chessboard.play_sound((y, x))
        elif y2 == y + 1:
            chessboard.board[y][x] = Rook(WHITE, chessboard)
            chessboard.play_sound((y, x))
        elif y2 == y:
            chessboard.board[y][x] = Queen(WHITE, chessboard)
            chessboard.play_sound((y, x))
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        chessboard.valid_white_moves[(x, y)] = chessboard.at(x, y).get_valid_moves((x, y))
        for nx, ny, _ in chessboard.valid_white_moves[(x, y)]:
            chessboard.invalid_black_king_moves.append((nx, ny))
        x, y = chessboard.black_king
        chessboard.valid_black_moves[(x, y)] = chessboard.at(x, y).get_valid_moves((x, y))
        chessboard.calculate_valid_moves(WHITE)
    else:
        return False
    promotion_in_progress = False
    promotion_pos = None
    promotion_color = None
    change = True
    return True

chessboard.on('win', determine_winner)
chessboard.on('promote', promote_pawn)

def draw():
    screen.fill(WHITE)
    tiles = chessboard.create()
    for tile in tiles:
        c, tup = tile
        pg.draw.rect(screen, c, tup)
    
    if selected_piece_pos:
        px, py = selected_piece_pos
        pg.draw.rect(screen, YELLOW, (px * TILE, py * TILE, TILE, TILE))
        for x, y, p in chessboard.at(px, py).get_cached_valid_moves(selected_piece_pos):
            if p == 0:
                pg.draw.circle(screen, GRAY, (x * TILE + 10 + 15, y * TILE + 10 + 15), 8)
            elif p == 1:
                pg.draw.rect(screen, RED, (x * TILE, y * TILE, TILE, TILE))
            elif p == -1:
                pass
    draw_pieces()

def draw_pieces():
    for i in range(len(chessboard.board)):
        for j in range(len(chessboard.board[i])):
            piece = chessboard.at(j, i)
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

def main():
    global selected_piece_pos, change
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save(filename="model.pth")
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pg.mouse.get_pos()
                    x = mouse_pos[0] // TILE
                    y = mouse_pos[1] // TILE
                    if promotion_in_progress:
                        saved_prom_pos = promotion_pos
                        if handle_promotion(*promotion_pos, promotion_color):
                            chessboard.recv(saved_prom_pos)
                    else:
                        if selected_piece_pos:
                            new_pos = (x, y)
                            chessboard.move_piece(selected_piece_pos, new_pos)
                            selected_piece_pos = None
                            change = True
                        else:
                            if chessboard.at(x, y) != None:
                                selected_piece_pos = (x, y)
                                change = True
        if change:
            draw()
            change = False
        if promotion_in_progress:
            if promotion_color != BLACK:
                draw_promotion_options(promotion_pos)
        pg.display.update()
        clock.tick(FPS)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
