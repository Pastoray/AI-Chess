from constants import WHITE, BLACK
import os

PIECE_ABBREVIATIONS = {
    "Pawn": "p",
    "Bishop": "b",
    "Knight": "n",
    "Rook": "r",
    "Queen": "q",
    "King": "k"
}

def load_image_path(piece, color):
    folder_path = "./assets/images"
    ext = ""
    if color == WHITE:
        ext = "l"
    elif color == BLACK:
        ext = "d"
    p = PIECE_ABBREVIATIONS.get(piece, "")
    path = f"Chess_{p}{ext}t45.svg"
    image_path = os.path.join(folder_path, path)

    return image_path