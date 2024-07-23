import torch
import torch.nn as nn
import torch.optim as optim
from logger import logger
import os
class ChessAI(nn.Module):
    def __init__(self):
        super(ChessAI, self).__init__()
        self.fc1 = nn.Linear(64 + 4, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
    
    def forward(self, board, move):
        x = torch.cat((board, move), dim=1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = ChessAI()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

def train(board, reward, model=model, criterion=criterion, optimizer=optimizer):
    model.train()

    board_tensor = torch.tensor(board, dtype=torch.float32).flatten().unsqueeze(0)  # Shape: (1, 64)
    move_tensor = torch.zeros((1, 4), dtype=torch.float32)
    output = model(board_tensor, move_tensor)
    
    loss = criterion(output, torch.tensor([reward], dtype=torch.float32).unsqueeze(0))

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

def choose(board, valid_moves):
    model.eval()
    board_tensor = torch.tensor(board, dtype=torch.float32).flatten().unsqueeze(0)  # Shape: (1, 64)
    bestMove = None
    bestScore = -float("inf")
    with torch.no_grad():
        for move in valid_moves:
            move_tensor = torch.tensor(move, dtype=torch.float32).unsqueeze(0)  # Shape: (1, 4)
            output = model(board_tensor, move_tensor)
            if output.item() > bestScore:
                bestMove = move
    return bestMove

def save(model=model, filename='model.pth'):
    torch.save(model.state_dict(), filename)
    logger.success(f"Model saved to {filename}")

def load(model=model, filename='model.pth'):
    if os.path.isfile(filename):
        try:
            model.load_state_dict(torch.load(filename))
            model.eval()
            logger.success(f"Model loaded from {filename}")
        except Exception as e:
            logger.error(f"Failed to load model from {filename}: {e}")
            model = ChessAI()
    else:
        logger.warn(f"Model file {filename} does not exist.")
        model = ChessAI()
