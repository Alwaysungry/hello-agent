# src/infer.py
import torch
from model import TransformerLM
from tokenizer import CharTokenizer
from config import Config

def load_tokenizer(stoi):
    tok = CharTokenizer("")  # dummy
    tok.stoi = stoi
    tok.itos = {i: ch for ch, i in stoi.items()}
    tok.vocab_size = len(stoi)
    return tok

def main():
    cfg = Config()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = torch.load("ckpt.pt", map_location=device)
    stoi = ckpt["tok"]
    tok = load_tokenizer(stoi)

    model = TransformerLM(
        vocab_size=tok.vocab_size,
        d_model=cfg.d_model,
        n_heads=cfg.n_heads,
        d_ff=cfg.d_ff,
        n_layers=cfg.n_layers,
        block_size=cfg.block_size,
        dropout=cfg.dropout,
    ).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()

    prompt = "智能体是"
    idx = torch.tensor([tok.encode(prompt)], dtype=torch.long).to(device)
    out = model.generate(idx, max_new_tokens=200)
    print(tok.decode(out[0].tolist()))

if __name__ == "__main__":
    main()
