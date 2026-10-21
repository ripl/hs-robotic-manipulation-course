import argparse
import glob
import json
#import numpy as np
import os
#import pandas as pd
import datetime
import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.utils.data import random_split
from tqdm import trange

NUM_SQUARES = 9

class GraspDataset(Dataset):
    def __init__(self, labels_dir, img_size=(640, 360)):
        """img_size: fallback (w, h) for labels saved before generate_data.py recorded 'img_size'."""
        all_paths = sorted(glob.glob(os.path.join(labels_dir, '*.json')))
        if not all_paths:
            raise ValueError(f"No .json files found in {labels_dir}")

        # Skip samples where SimVision found no piece: vision.py doesn't run the model without a bbox
        self.label_paths = []
        for path in all_paths:
            with open(path, 'r') as f:
                if json.load(f).get('vision_piece_bbox') is not None:
                    self.label_paths.append(path)
        n_skipped = len(all_paths) - len(self.label_paths)
        if n_skipped:
            print(f"Skipping {n_skipped} samples with no detected bbox")
        if not self.label_paths:
            raise ValueError(f"No samples with a detected bbox in {labels_dir}")

        self.num_squares = NUM_SQUARES
        self.img_w, self.img_h = img_size

        print(f"Successfully loaded {len(self.label_paths)} .json files!")

    def __len__(self):
        return len(self.label_paths)

    def __getitem__(self, idx):
        with open(self.label_paths[idx], 'r') as f:
            row = json.load(f)

        # --- square index -> one-hot ---
        square_idx = int(row['square_idx'])
        square_onehot = F.one_hot(
            torch.tensor(square_idx), num_classes=self.num_squares
        ).float()

        # --- bbox: (x, y, w, h) in pixels, or None if not detected ---
        bbox = row['vision_piece_bbox']

        img_w, img_h = row.get('img_size', (self.img_w, self.img_h))

        if bbox is not None:
            x, y, w, h = bbox
            bbox_norm = torch.tensor([
                x / img_w,
                y / img_h,
                w / img_w,
                h / img_h,
            ], dtype=torch.float32)
            bbox_missing = torch.tensor([0.0])
        else:
            # set missing flag
            bbox_norm = torch.zeros(4, dtype=torch.float32)
            bbox_missing = torch.tensor([1.0])

        x_tensor = torch.cat([square_onehot, bbox_norm, bbox_missing])

        # --- labels: grid_size x grid_size binary grid ---
        labels = torch.tensor(row['labels'], dtype=torch.float32)

        return x_tensor, labels

class GraspMLP(nn.Module):
    def __init__(self, grid_size=7, hidden_dim=256, dropout=0.3):
        super().__init__()
        self.grid_size = grid_size
        input_dim = NUM_SQUARES + 4 + 1  # one-hot square + (x, y, w, h) bbox + missing flag

        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, grid_size * grid_size),
        )

    def forward(self, x):
        logits = self.net(x)
        return logits.view(-1, self.grid_size, self.grid_size)

def train_one_epoch(model, loader, optimizer, loss_fn, device):
    running_loss = 0.0
    for x_tensor, labels in loader:
        x_tensor, labels = x_tensor.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(x_tensor)
        loss = loss_fn(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * x_tensor.size(0)
    return running_loss / len(loader.dataset)

def train(model: GraspMLP, dataset, optimizer, loss_fn, device, n_epochs=5000, patience=50,
          batch_size=32, val_frac=0.15, num_workers=4, models_dir='models', seed=0):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    os.makedirs(models_dir, exist_ok=True)

    model.train(True)

    best_vloss = 1_000_000.
    best_path = None

    epochs_since_improvement = 0

    n_val = max(1, int(val_frac * len(dataset)))
    n_train = len(dataset) - n_val
    split_gen = torch.Generator().manual_seed(seed)  # same split for the same seed
    train_dataset, val_dataset = random_split(dataset, [n_train, n_val], generator=split_gen)
    print(f"{n_train} train / {n_val} val samples")
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    for epoch in trange(n_epochs):
        model.train(True)
        avg_loss = train_one_epoch(model, train_loader, optimizer, loss_fn, device)

        running_vloss = 0.0
        model.eval()

        with torch.no_grad():
            for x_tensor, labels in val_loader:
                x_tensor, labels = x_tensor.to(device), labels.to(device)
                outputs = model(x_tensor)
                vloss = loss_fn(outputs, labels)
                running_vloss += vloss.item() * x_tensor.size(0)

        avg_vloss = running_vloss / len(val_loader.dataset)

        if avg_vloss < best_vloss:
            best_vloss = avg_vloss
            best_path = os.path.join(models_dir, f'model_{timestamp}_{epoch}.pt')
            epochs_since_improvement = 0
            torch.save(model.state_dict(), best_path)
        else:
            epochs_since_improvement += 1
            if epochs_since_improvement > patience:
                print(f"Early stopping at epoch {epoch} with loss {best_vloss}")
                break

        if epoch % 10 == 0:
            print(f"Epoch {epoch}: train_loss={avg_loss:.4f}, val_loss={avg_vloss:.4f}")

    print(f"Best val_loss {best_vloss:.4f}: {best_path}")
    return model

def parse_args():
    # Defaults match the values this script used before it took arguments
    parser = argparse.ArgumentParser(description="Train the grasp-grid MLP.")
    parser.add_argument('--labels_dir', default='dataset/labels/', help="Directory of label .json files.")
    parser.add_argument('--models_dir', default='models', help="Where checkpoints are saved.")
    parser.add_argument('--epochs', type=int, default=5000)
    parser.add_argument('--patience', type=int, default=50, help="Epochs without val improvement before stopping.")
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--weight_decay', type=float, default=1e-2)
    parser.add_argument('--hidden_dim', type=int, default=256,
                        help="Hidden layer width. vision.py builds GraspMLP with the default, so change both together.")
    parser.add_argument('--dropout', type=float, default=0.3)
    parser.add_argument('--val_frac', type=float, default=0.15)
    parser.add_argument('--num_workers', type=int, default=4)
    parser.add_argument('--seed', type=int, default=0, help="Seeds weight init and the train/val split.")
    parser.add_argument('--device', choices=['auto', 'cuda', 'mps', 'cpu'], default='auto')
    return parser.parse_args()

def main():
    args = parse_args()
    torch.manual_seed(args.seed)
    dataset = GraspDataset(args.labels_dir)

    device = args.device
    if device == 'auto':
        if torch.cuda.is_available():
            device = 'cuda'
        elif torch.backends.mps.is_available():
            device = 'mps'
        else:
            device = 'cpu'
    print(f"Training on {device}")
    print("Hyperparameters:", vars(args))
    model = GraspMLP(grid_size=7, hidden_dim=args.hidden_dim, dropout=args.dropout).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    loss_fn = nn.BCEWithLogitsLoss()

    model = train(model, dataset, optimizer, loss_fn, device=device, n_epochs=args.epochs,
                  patience=args.patience, batch_size=args.batch_size, val_frac=args.val_frac,
                  num_workers=args.num_workers, models_dir=args.models_dir, seed=args.seed)

if __name__ == "__main__":
    main()
