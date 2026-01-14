# src/train.py
import os
import torch
import numpy as np
import pdfplumber
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from config import Config
from tokenizer import CharTokenizer
from model import TransformerLM

class TextDataset(Dataset):
    def __init__(self, ids, block_size):
        self.ids = ids
        self.block_size = block_size
    def __len__(self): return len(self.ids) - self.block_size
    def __getitem__(self, i):
        x = torch.tensor(self.ids[i:i+self.block_size], dtype=torch.long)
        y = torch.tensor(self.ids[i+1:i+1+self.block_size], dtype=torch.long)
        return x, y

def main():
    cfg = Config()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg.device = device

    import pdfplumber

    with pdfplumber.open("data/LLMBook.pdf") as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""


    tok = CharTokenizer(text)
    ids = tok.encode(text)
    cfg.vocab_size = tok.vocab_size

    ds = TextDataset(ids, cfg.block_size)
    dl = DataLoader(ds, batch_size=cfg.batch_size, shuffle=True, drop_last=True)

    model = TransformerLM(
        vocab_size=cfg.vocab_size,
        d_model=cfg.d_model,
        n_heads=cfg.n_heads,
        d_ff=cfg.d_ff,
        n_layers=cfg.n_layers,
        block_size=cfg.block_size,
        dropout=cfg.dropout,
    ).to(device)

    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr)
    scaler = torch.cuda.amp.GradScaler(enabled=(device == "cuda"))

    model.train()
    pbar = tqdm(range(cfg.max_steps), desc="training")
    it = iter(dl)
    for step in pbar:
        try:
            x, y = next(it)
        except StopIteration:
            it = iter(dl)
            x, y = next(it)

        x, y = x.to(device), y.to(device)

        with torch.cuda.amp.autocast(enabled=(device == "cuda")):
            logits = model(x)
            loss = torch.nn.functional.cross_entropy(logits.view(-1, cfg.vocab_size), y.view(-1))

        scaler.scale(loss).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt)
        scaler.update()
        opt.zero_grad(set_to_none=True)

        pbar.set_postfix(loss=float(loss.item()))

        if (step + 1) % 200 == 0:
            torch.save({
                "model": model.state_dict(),
                "tok": tok.stoi,                # 保存词表映射
            }, "ckpt.pt")

    print("done.")

if __name__ == "__main__":
    main()
