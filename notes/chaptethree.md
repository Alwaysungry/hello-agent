# 大语言模型基础

## 语言模型与 Transformer 架构

### 从 N-gram 到 RNN

语言模型任务：计算一个词序列出现的概率。

- N-gram 模型：基于马尔可夫假设，只考虑前 n-1 个词。

    例子：Bigram 模型计算 P(agent | datawhale)，通过词对出现次数估计。

    缺陷：数据稀疏、无法泛化语义相似性。

- 神经网络语言模型：引入词嵌入，词用向量表示。

    例子：vector("King") - vector("Man") + vector("Woman") ≈ vector("Queen")，展示了词向量的语义关系。

    RNN/LSTM：引入隐藏状态，解决固定窗口问题。

    例子：RNN 在长序列中会遇到梯度消失，LSTM 通过遗忘门、输入门、输出门缓解。

### Transformer 架构解析

核心思想：完全抛弃循环结构，依赖**注意力机制**实现并行计算。

Encoder-Decoder 结构：

- 编码器：理解输入序列。

- 解码器：生成输出序列。

- 自注意力机制 (Self-Attention)：每个词通过 Query、Key、Value 与其他词交互。

    公式：$$ Attention(Q,K,V) = softmax\left(\frac{QK^T}{\sqrt{d_k}}\right)V $$

    例子：句子 “The agent learns because it is intelligent.” 中，it 会关注 agent。

- 多头注意力 (Multi-Head Attention)：并行计算多个注意力，捕捉不同关系。

- 前馈网络 (FFN)：逐位置独立处理，提取高阶特征。

- 残差连接与层归一化：保证深层网络稳定训练。

- 位置编码 (Positional Encoding)：用正弦/余弦函数引入位置信息。

    例子：agent learns 与 learns agent 在自注意力中等价，但位置编码能区分。

### Decoder-Only 架构

思想：只保留解码器，专注于预测下一个词。

- 自回归生成：模型不断基于已有文本预测下一个词。

    例子：输入 “Datawhale Agent is”，模型生成 “a powerful system”。

- 掩码自注意力：保证预测第 t 个词时不能看到未来词。

优势：

- 训练目标统一（预测下一个词）。

- 结构简单，易扩展。

- 天然适合生成任务。

代表模型：GPT 系列、LLaMA、Qwen。

## 与大语言模型交互

### 提示工程 (Prompt Engineering)

采样参数：

- Temperature：控制随机性。

    例子：T=0.2 → 输出更确定；T=1.0 → 输出更多样。

- Top-k：只保留概率最高的 k 个候选。

- Top-p：动态选择累计概率 ≥ p 的集合。

提示类型：

- 零样本 (Zero-shot)：直接指令。

    例子：文本 “Datawhale的课程非常棒！” → 情感分类为正面。

- 单样本 (One-shot)：提供一个示例。

- 少样本 (Few-shot)：提供多个示例，提升准确性。

指令调优 (Instruction Tuning)：

    让模型更好理解自然语言指令。

    技巧：角色扮演、上下文示例、思维链 (CoT)。

    例子：篮球队胜率计算，通过 “一步一步思考” 提示，模型能正确推理。

### 文本分词

作用：将文本转为模型可处理的 Token。

方法：

    按词分词：词表过大，OOV 问题严重。

    按字符分词：词表小，但语义弱。

    子词分词 (Subword)：兼顾词表大小与语义。

算法：

    BPE (Byte-Pair Encoding)：迭代合并高频词元对。

    例子：hug, pug, bun → 合并 u+g → ug。

    WordPiece：最大化语言模型概率。

    SentencePiece：空格也作为字符，语言无关。

开发者意义：影响上下文窗口、API 成本、模型表现。

    例子：2+2 与 2 + 2 分词不同，可能导致模型计算错误。


### 模型的选择

考量因素：性能、成本、速度、上下文窗口、部署方式、生态、可微调性、安全性。

闭源模型：GPT、Gemini、Claude、国内文心一言、混元等。

开源模型：LLaMA、Mistral、Qwen、ChatGLM。

例子：

GPT-5：多模态、实时语音对话。

Gemini 2.5 Flash：快速推理，适合低延迟场景。

LLaMA 4 Scout：支持千万级 Token 上下文。

## 大语言模型的缩放法则与局限性

### 缩放法则 (Scaling Laws)

    规律：性能随参数规模、数据量、计算量的增加而提升。

    例子：GPT-3 → 175B 参数，能力显著超越 GPT-2。

### 模型幻觉 (Hallucination)

    问题：模型可能生成看似合理但错误的信息。

    例子：模型回答 “爱因斯坦获得过诺贝尔和平奖”，实际上是错误的。

    解决思路：检索增强、事实校验、外部工具调用。

## 本章小结

- 大语言模型的发展经历了 N-gram → 神经网络 → RNN/LSTM → Transformer → Decoder-Only 架构。

- 交互方式依赖提示工程、分词、模型调用与选择。

- 缩放法则推动了模型能力提升，但幻觉问题仍是挑战。

- 例子串联：

    Bigram → P(agent | datawhale)

    词向量 → King - Man + Woman ≈ Queen

    LSTM → 解决长期依赖

    Transformer → 自注意力捕捉全局关系

    GPT → 自回归生成

    Qwen → 本地开源对话

    GPT-5/Gemini → 多模态与实时交互