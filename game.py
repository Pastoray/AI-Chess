import pygame as pg
from constants import *
from collections import defaultdict

class ChessBoard:
    _instance = None
    def __init__(self, turn, tile):
        self.turn = turn
        self.tile = tile
        self.board = self.init_board()
        self.white_king, self.black_king = self.init_kings()
        self.valid_white_moves, self.valid_black_moves = {}, {}
        self.invalid_white_king_moves, self.invalid_black_king_moves = [], []
        self.white_pawn_promoted, self.black_pawn_promoted = False, False
        self.winner = False
        self.moves_with_no_capturing = 0
        self.positions = defaultdict(int)
        self.positions[tuple(tuple(row) for row in self.board)] = 1

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def init_kings(self):
        white_king = None
        black_king = None
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if (self.board[i][j] and
                    self.board[i][j].name() == KING and
                    self.board[i][j].color == BLACK):
                    
                    black_king = (j, i)

                elif (self.board[i][j] and
                    self.board[i][j].name() == KING and
                    self.board[i][j].color == WHITE):

                    white_king = (j, i)
        return [white_king, black_king]

    def init_board(self):
        return [
            [Rook(BLACK, self), Knight(BLACK, self), Bishop(BLACK, self), Queen(BLACK, self), King(BLACK, self), Bishop(BLACK, self), Knight(BLACK, self), Rook(BLACK, self)],
            [Pawn(BLACK, self), Pawn(BLACK, self), Pawn(BLACK, self), Pawn(BLACK, self), Pawn(BLACK, self), Pawn(BLACK, self), Pawn(BLACK, self), Pawn(BLACK, self)],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [Pawn(WHITE, self), Pawn(WHITE, self), Pawn(WHITE, self), Pawn(WHITE, self), Pawn(WHITE, self), Pawn(WHITE, self), Pawn(WHITE, self), Pawn(WHITE, self)],
            [Rook(WHITE, self), Knight(WHITE, self), Bishop(WHITE, self), Queen(WHITE, self), King(WHITE, self), Bishop(WHITE, self), Knight(WHITE, self), Rook(WHITE, self)]
        ]
    
    def reset(self):
        self.turn = WHITE
        self.board = self.init_board() 
        self.white_king, self.black_king = self.init_kings()
        self.valid_white_moves, self.valid_black_moves = {}, {}
        self.invalid_white_king_moves, self.invalid_black_king_moves = [], []
        self.white_pawn_promoted, self.black_pawn_promoted = False, False
        self.winner = False
        self.moves_with_no_capturing = 0
        self.positions = defaultdict(int)
        self.positions[tuple(tuple(row) for row in self.board)] = 1

    def is_valid_move(self, curr_pos, new_pos):
        x, y = curr_pos
        new_x, new_y = new_pos
    
        if (self.get_piece(x, y).color == self.turn and
            (self.get_piece(new_x, new_y) == None or
            self.get_piece(x, y).color != self.get_piece(new_x, new_y).color) and
            self.get_piece(x, y).is_valid_move(curr_pos, new_pos)):

            return True
        return False
    
    def castle(self, curr_pos, new_pos):
        x, y = curr_pos
        new_x, new_y = new_pos
        if self.get_piece(x, y).name() == KING and self.get_piece(x, y).color == WHITE:
            if x - new_x == 2:
                self.board[y][0] = None
                self.board[y][new_x + 1] = Rook(WHITE, self)
            elif x - new_x == -2:
                self.board[y][len(self.board) - 1] = None
                self.board[y][new_x - 1] = Rook(WHITE, self)
            self.white_king = (new_x, new_y)
        elif self.get_piece(x, y).name() == KING and self.get_piece(x, y).color == BLACK:
            if x - new_x == 2:
                self.board[y][0] = None
                self.board[y][new_x + 1] = Rook(BLACK, self)
            elif x - new_x == -2:
                self.board[y][len(self.board) - 1] = None
                self.board[y][new_x - 1] = Rook(BLACK, self)
            self.black_king = (new_x, new_y)

    def fifty_move_rule(self, new_pos):
        new_x, new_y = new_pos
        if self.board[new_y][new_x]:
            self.moves_with_no_capturing = 0
            self.positions[tuple(tuple(row) for row in self.board)] = 1
        else:
            self.moves_with_no_capturing += 1
        if self.moves_with_no_capturing == 50:
            self.winner = None
    def threefold_repetition_rule(self):
        self.positions[tuple(tuple(row) for row in self.board)] += 1

        if max(self.positions.values()) >= 3:
            self.winner = None

    def calculate_invalid_king_moves(self, color=None):
        if not color:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == BLACK:
                        piece = self.get_piece(j, i)
                        movements = []
                        if piece.name() == PAWN:
                            self.invalid_white_king_moves.append((j - 1, i + 1))
                            self.invalid_white_king_moves.append((j + 1, i + 1))
                        elif piece.name() == KING:
                            movements = piece.get_valid_moves((j, i), True)
                        else:
                            movements = piece.get_valid_moves((j, i))
                        for x, y, _ in movements:
                            self.invalid_white_king_moves.append((x, y))
                    elif self.get_piece(j, i) and self.get_piece(j, i).color == WHITE:
                        piece = self.get_piece(j, i)
                        movements = []
                        if piece.name() == PAWN:
                            self.invalid_black_king_moves.append((j - 1, i - 1))
                            self.invalid_black_king_moves.append((j + 1, i - 1))
                        elif piece.name() == KING:
                            movements = piece.get_valid_moves((j, i), True)
                        else: 
                            movements = piece.get_valid_moves((j, i))
                        for x, y, _ in movements:
                            self.invalid_black_king_moves.append((x, y))
        elif color == WHITE:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == BLACK:
                        piece = self.get_piece(j, i)
                        movements = []
                        if piece.name() == PAWN:
                            self.invalid_white_king_moves.append((j - 1, i + 1))
                            self.invalid_white_king_moves.append((j + 1, i + 1))
                        elif piece.name() == KING:
                            movements = piece.get_valid_moves((j, i), True)
                        else:
                            movements = piece.get_valid_moves((j, i))
                        for x, y, _ in movements:
                            self.invalid_white_king_moves.append((x, y))
        elif color == BLACK:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == WHITE:
                        piece = self.get_piece(j, i)
                        movements = []
                        if piece.name() == PAWN:
                            self.invalid_black_king_moves.append((j - 1, i - 1))
                            self.invalid_black_king_moves.append((j + 1, i - 1))
                        elif piece.name() == KING:
                            movements = piece.get_valid_moves((j, i), True)
                        else: 
                            movements = piece.get_valid_moves((j, i))
                        for x, y, _ in movements:
                            self.invalid_black_king_moves.append((x, y))

    def calculate_valid_moves(self, color=None):
        if color == None:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == WHITE:
                        if self.get_piece(j, i).name() != KING:
                            self.valid_white_moves[(j, i)] = self.valid_blocking_moves((i, j), WHITE)
                        else:
                            self.valid_white_moves[(j, i)] = []
                            piece_movements = self.get_piece(j, i).get_valid_moves((j, i))
                            for x, y, p in piece_movements:
                                if p != -1:
                                    self.valid_white_moves[(j, i)].append((x, y, p))
            self.determine_loss(WHITE)

            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == BLACK:
                        if self.get_piece(j, i).name() != KING:
                            self.valid_black_moves[(j, i)] = self.valid_blocking_moves((i, j), BLACK)
                        else:
                            self.valid_black_moves[(j, i)] = []
                            piece_movements = self.get_piece(j, i).get_valid_moves((j, i))
                            for x, y, p in piece_movements:
                                if p != -1:
                                    self.valid_black_moves[(j, i)].append((x, y, p))
            self.determine_loss(BLACK)

        elif color == WHITE:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == WHITE:
                        if self.get_piece(j, i).name() != KING:
                            self.valid_white_moves[(j, i)] = self.valid_blocking_moves((i, j), WHITE)
                        else:
                            self.valid_white_moves[(j, i)] = []
                            piece_movements = self.get_piece(j, i).get_valid_moves((j, i))
                            for x, y, p in piece_movements:
                                if p != -1:
                                    self.valid_white_moves[(j, i)].append((x, y, p))
            self.determine_loss(WHITE)

        elif color == BLACK:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == BLACK:
                        if self.get_piece(j, i).name() != KING:
                            self.valid_black_moves[(j, i)] = self.valid_blocking_moves((i, j), BLACK)
                        else:
                            self.valid_black_moves[(j, i)] = []
                            piece_movements = self.get_piece(j, i).get_valid_moves((j, i))
                            for x, y, p in piece_movements:
                                if p != -1:
                                    self.valid_black_moves[(j, i)].append((x, y, p))
            self.determine_loss(BLACK)

    def determine_loss(self, color):
        if color == WHITE:
            if len(max(self.valid_white_moves.values(), key=len)) == 0:
                if self.white_king in self.invalid_white_king_moves:
                    self.winner = BLACK
                    return True
            return False
        elif color == BLACK:
            if len(max(self.valid_black_moves.values(), key=len)) == 0:
                if self.black_king in self.invalid_black_king_moves:
                    self.winner = WHITE
                    return True
            return False
    def move_piece(self, curr_pos, new_pos):
        if self.is_valid_move(curr_pos, new_pos):
            x, y = curr_pos
            new_x, new_y = new_pos
            
            self.play_sound(new_pos)
            self.castle(curr_pos, new_pos)

            self.fifty_move_rule(new_pos)
            
            self.board[new_y][new_x] = self.get_piece(x, y)
            self.board[y][x] = None

            self.threefold_repetition_rule()
            self.promote_pawn()
            
            self.invalid_white_king_moves, self.invalid_black_king_moves = [], []
            self.valid_white_moves, self.valid_black_moves = {}, {}

            self.calculate_invalid_king_moves()
            self.calculate_valid_moves()

            self.turn = WHITE if self.turn == BLACK else BLACK

    def valid_blocking_moves(self, pos, color):
        i1, j1 = pos
        checked_by = 0
        piece = self.get_piece(j1, i1)
        if color == WHITE:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == BLACK and self.white_king in self.get_piece(j, i).get_valid_moves((j, i)):
                        checked_by += 1
            valid_moves = []
            for x, y, p in piece.get_valid_moves((j1, i1)):
                if p != -1:
                    temp = self.get_piece(x, y)
                    self.board[y][x] = piece
                    self.board[i1][j1] = None
                    temp_checked_by = 0
                    for k in range(len(self.board)):
                        for l in range(len(self.board[k])):
                            if self.board[k][l] and self.board[k][l].color == BLACK:
                                opp_piece = self.get_piece(l, k)
                                for x2, y2, _ in opp_piece.get_valid_moves((l, k)):
                                    if self.white_king == (x2, y2):
                                        temp_checked_by += 1

                    if temp_checked_by <= checked_by:
                        valid_moves.append((x, y, p))

                    self.board[y][x] = temp
                    self.board[i1][j1] = piece
        elif color == BLACK:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.get_piece(j, i) and self.get_piece(j, i).color == WHITE and self.black_king in self.get_piece(j, i).get_valid_moves((j, i)):
                        checked_by += 1
            valid_moves = []
            for x, y, p in piece.get_valid_moves((j1, i1)):
                if p != -1:
                    temp = self.get_piece(x, y)
                    self.board[y][x] = piece
                    self.board[i1][j1] = None
                    temp_checked_by = 0
                    for k in range(len(self.board)):
                        for l in range(len(self.board[k])):
                            if self.board[k][l] and self.board[k][l].color == WHITE:
                                opp_piece = self.get_piece(l, k)
                                for x2, y2, _ in opp_piece.get_valid_moves((l, k)):
                                    if self.black_king == (x2, y2):
                                        temp_checked_by += 1

                    if temp_checked_by <= checked_by:
                        valid_moves.append((x, y, p))

                    self.board[y][x] = temp
                    self.board[i1][j1] = piece
        return valid_moves
    
    def promote_pawn(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.get_piece(j, i) and self.get_piece(j, i).name() == PAWN:
                    if self.get_piece(j, i).color == BLACK and i == 7:
                        self.black_pawn_promoted = (j, i)

                    elif self.get_piece(j, i).color == WHITE and i == 0:
                        self.white_pawn_promoted = (j, i)

    def get_piece(self, x, y):
        if 0 <= y < len(self.board) and 0 <= x < len(self.board[0]): 
            return self.board[y][x]
        return None
    
    def play_sound(self, pos):
        x, y = pos
        if self.get_piece(x, y) == None:
            sound = pg.mixer.Sound(MOVE_PIECE_SOUND)
            sound.set_volume(0.5)
        else:
            sound = pg.mixer.Sound(CAPTURE_PIECE_SOUND)
            sound.set_volume(0.3)
        sound.play()

    def create(self):
        tiles = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                color = ROSE if (i + j) % 2 == 0 else WHITE
                tiles.append((color, (i * self.tile, j * self.tile, self.tile, self.tile)))
        return tiles
    
    def get_winner(self):
        return self.winner

class Piece:
    def __init__(self, color, board):
        self.chessboard = board
        self.color = color

    def is_valid_move(self, curr_pos, new_pos):      
        valid_moves = self.get_cached_valid_moves(curr_pos)
        for x, y, _ in valid_moves:
            if new_pos == (x, y):
                return True
        return False
    
    def get_cached_valid_moves(self, pos):
        if self.color == WHITE and len(self.chessboard.valid_white_moves) != 0:
            return self.chessboard.valid_white_moves[pos]
        elif self.color == BLACK and len(self.chessboard.valid_black_moves) != 0:
            return self.chessboard.valid_black_moves[pos]
        else:
            return self.get_valid_moves(pos)

    def get_valid_moves(self, pos):
        pass

    def name(self):
        return self.__class__.__name__

    def in_bound(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

class Pawn(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)
        self.has_moved = False
    def is_valid_move(self, curr_pos, new_pos):
        valid_moves = self.get_cached_valid_moves(curr_pos)
        for x, y, _ in valid_moves:
            if new_pos == (x, y):
                if not self.has_moved:
                    self.has_moved = True
                return True
        return False
    
    def get_valid_moves(self, pos):
        x, y = pos
        movements = []
        m = 1 if self.color == BLACK else -1
        for i in range(1, 2 + (not self.has_moved)):
            if not self.in_bound(x, y + i * m) or self.chessboard.get_piece(x, y + i * m):
                break
            movements.append((x, y + i * m, 0))
        for i in [-1, 1]:
            if self.in_bound(x + i, y + 1):
                piece = self.chessboard.get_piece(x + i, y + 1 * m)
                if piece and piece.color != self.color:
                    movements.append((x + i, y + 1 * m, 1))
        return movements
    
class Bishop(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)
    def get_valid_moves(self, pos):
        x, y = pos
        movements = []
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            for i in range(1, 8):
                ny, nx = y + (i * dy) , x + (i * dx)
                if not self.in_bound(ny, nx):
                    break
                if self.chessboard.board[ny][nx] and self.chessboard.board[ny][nx].color != self.color:
                    movements.append((nx, ny, 1))
                    if self.chessboard.board[ny][nx].name() == KING:
                        for i in range(i + 1, 8):
                            ny, nx = y + (i * dy), x + (i * dx)
                            if not self.in_bound(ny, nx) or self.chessboard.board[ny][nx]:
                                break
                            movements.append((nx, ny, -1))
                    break
                elif self.chessboard.board[ny][nx] and self.chessboard.board[ny][nx].color == self.color:
                    movements.append((nx, ny, -1))
                    break
                else:
                    movements.append((nx, ny, 0))
        return movements


class Knight(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)
    def get_valid_moves(self, pos):
        x, y = pos
        movements = []
        for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            nx, ny = x + dx, y + dy
            if self.in_bound(nx, ny):
                if self.chessboard.board[ny][nx] == None:
                    movements.append((nx, ny, 0))
                elif self.chessboard.board[ny][nx].color != self.color:
                    movements.append((nx, ny, 1))
                else:
                    movements.append((nx, ny, -1))
        return movements
    
class Rook(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)
        self.has_moved = False

    def is_valid_move(self, curr_pos, new_pos):
        valid_moves = self.get_cached_valid_moves(curr_pos)
        for x, y, _ in valid_moves:
            if new_pos == (x, y):
                if not self.has_moved:
                    self.has_moved = True
                return True
        return False
    
    def get_valid_moves(self, pos):
        x, y = pos
        movements = []
        for i, (start, end, step) in enumerate([(x - 1, -1, -1), (x + 1, 8, 1), (y - 1, -1, -1), (y + 1, 8, 1)]):
            for j in range(start, end, step):
                nx = j if i <= 1 else x
                ny = j if i > 1 else y
                if self.chessboard.get_piece(nx, ny) and self.chessboard.get_piece(nx, ny).color != self.color:
                    movements.append((nx, ny, 1))
                    if self.chessboard.get_piece(nx, ny).name() == KING:
                        nx = j + step if i <= 1 else x
                        ny = j + step if i > 1 else y
                        while self.in_bound(nx, ny):
                            if self.chessboard.get_piece(nx, ny):
                                break
                            movements.append((nx, ny, -1))
                            if i <= 1:
                                nx += step
                            else:
                                ny += step
                    break
                elif self.chessboard.get_piece(nx, ny) and self.chessboard.get_piece(nx, ny).color == self.color:
                    movements.append((nx, ny, -1))
                    break
                else:
                    movements.append((nx, ny, 0))
        return movements

class Queen(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)
    def get_valid_moves(self, pos):
        x, y = pos
        movements = []
        for i, (start, end, step) in enumerate([(x - 1, -1, -1), (x + 1, 8, 1), (y - 1, -1, -1), (y + 1, 8, 1)]):
            for j in range(start, end, step):
                nx = j if i <= 1 else x
                ny = j if i > 1 else y
                if self.chessboard.get_piece(nx, ny) and self.chessboard.get_piece(nx, ny).color != self.color:
                    movements.append((nx, ny, 1))
                    if self.chessboard.get_piece(nx, ny) == KING:
                        nx = j + 1 if i <= 1 else x
                        ny = j + 1 if i > 1 else y
                        while self.in_bound(nx, ny):
                            if self.chessboard.get_piece(nx ,ny):
                                break
                            movements.append((nx, ny, -1))
                            if i <= 1:
                                nx += step
                            else:
                                ny += step
                    break
                elif self.chessboard.get_piece(nx, ny) and self.chessboard.get_piece(nx, ny).color == self.color:
                    movements.append((nx, ny, -1))
                    break
                else:
                    movements.append((nx, ny, 0))
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            for i in range(1, 8):
                ny, nx = y + (i * dy) , x + (i * dx)
                if not self.in_bound(ny, nx):
                    break
                if self.chessboard.get_piece(nx, ny) and self.chessboard.get_piece(nx, ny).color != self.color:
                    movements.append((nx, ny, 1))
                    if self.chessboard.get_piece(nx, ny).name() == KING:
                        for i in range(i + 1, 8):
                            ny, nx = y + (i * dy), x + (i * dx)
                            if not self.in_bound(ny, nx) or self.chessboard.board[ny][nx]:
                                break
                            movements.append((nx, ny, -1))
                    break
                elif self.chessboard.board[ny][nx] and self.chessboard.board[ny][nx].color == self.color:
                    movements.append((nx, ny, -1))
                    break
                else:
                    movements.append((nx, ny, 0))
        
        return movements

class King(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)
        self.has_moved = False

    def is_valid_move(self, curr_pos, new_pos):
        valid_moves = self.get_cached_valid_moves(curr_pos)
        for x, y, _ in valid_moves:
            if new_pos == (x, y):
                if not self.has_moved:
                    self.has_moved = True
                return True
        return False
    
    def get_valid_moves(self, pos, all=False):
        x, y = pos
        movements = []
        for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)]:
            if self.in_bound(nx, ny):
                if self.chessboard.get_piece(nx, ny) and self.chessboard.get_piece(nx, ny).color != self.color:
                    movements.append((nx, ny, 1))
                elif self.chessboard.get_piece(nx, ny) == None:
                    movements.append((nx, ny, 0))
                else:
                    movements.append((nx, ny, -1))

        if not self.has_moved:
            for nx in range(len(self.chessboard.board)):
                if self.chessboard.get_piece(nx, y):
                    if (nx == len(self.chessboard.board) - 1
                        and self.chessboard.get_piece(nx, y).name() == ROOK
                        and self.chessboard.get_piece(nx, y).color == self.color
                        and self.chessboard.get_piece(nx, y).has_moved == False
                        and self.in_bound(x + 2, y)
                        and self.chessboard.get_piece(x + 2, y) == None):

                        movements.append((x + 2, y, 0))

                    if (nx == 0
                        and self.chessboard.get_piece(nx, y).name() == ROOK
                        and self.chessboard.get_piece(nx, y).color == self.color
                        and self.chessboard.get_piece(nx, y).has_moved == False
                        and self.in_bound(x - 2, y)
                        and self.chessboard.get_piece(x - 2, y) == None):
                        
                        movements.append((x - 2, y, 0))

        if all:
            return movements
        else:
            return self.is_checked(movements, pos)
    
    def is_checked(self, movements, pos):
        j, i = pos
        invalid_moves = []
        if self.color == WHITE:
            invalid_moves = self.chessboard.invalid_white_king_moves
        elif self.color == BLACK:
            invalid_moves = self.chessboard.invalid_black_king_moves

        if (j + 1, i) in invalid_moves:
            for idx, (x2, y2, _) in enumerate(movements):
                if (j + 2, i) == (x2, y2):
                    movements.pop(idx)

        if (j - 1, i) in invalid_moves:
            for idx, (x2, y2, _) in enumerate(movements):
                if (j - 2, i) == (x2, y2):
                    movements.pop(idx)

        i = 0
        while i < len(movements):
            x, y, _ = movements[i]
            if (x, y) in invalid_moves:
                movements.pop(i)
            else:
                i += 1
        return movements
