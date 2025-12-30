# src/config.py
from dataclasses import dataclass

@dataclass
class Config:
    vocab_size: int = 1000         # 训练后会由 tokenizer 实际设置
    d_model: int = 256
    n_heads: int = 8
    d_ff: int = 1024
    n_layers: int = 4
    dropout: float = 0.1
    block_size: int = 128
    batch_size: int = 64
    max_steps: int = 2000
    lr: float = 3e-4
    device: str = "cuda"  # 自动切换：在 train.py 检测
