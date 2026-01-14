# 智能体经典范式构建

三种经典范式
- Reasoning and Acting (ReAct)：让智能体边想边做，动态调整
- Plan-and-Solve：让智能体先规划，再严格执行
- Reflection：让智能体“反思”，通过自我批判和修正优化结果

## ReAct

**推理（Reasoning）与行动（Act）**

核心思想：
- **思考**与**行动**是相辅相成的，思考指导行动，行动的结果反过来又修正思考。
- 形成思考->行动->观察的循环
- 调用外部工具，动态调整推理过程

工作流程：
- Thought（思考）：分析问题，制定计划，或者反思上一步的结果
- Action（行动）：采取具体动作，例如调用外部工具
- Observation（观察）：执行Action后从外部工具获取的结果
- 循环迭代，直到最终答案或者循环次数耗尽

特点：
- 高可解释性：能看到完整的推理链
- 动态纠错：可根据观察结果调整策略
- 工具协同：结合 LLM 推理与外部工具执行

局限性：
- 强依赖 LLM 的能力
- 执行效率低（需要多次调用）
- 提示词脆弱，容易出错
- 缺乏全局规划，可能陷入局部最优

适用场景：
- 需要外部知识的任务：例如查询实时信息
- 需要精确计算的任务：例如调用计算器计算
- 需要与API交互的任务：例如操作数据库、调用某个API来完成任务

## Plan-and-Solve

**规划**（Plan）与**求解**（Solve）

核心思想
- 先规划 (Plan) → 后执行 (Solve)
- 由 LLM 先生成完整的行动计划，再逐步执行
  
工作流程
- 规划阶段：分解问题，生成结构化步骤
- 执行阶段：逐步执行计划，传递上下文结果

应用场景：适合结构化、可分解的复杂任务
- 多步数学应用题：需要先列出计算步骤，再逐一求解。
- 需要整合多个信息源的报告撰写：需要先规划好报告结构（引言、数据来源A、数据来源B、总结），再逐一填充内容。
- 代码生成任务：需要先构思好函数、类和模块的结构，再逐一实现。

## Reflection

核心思想
- 引入 **事后反思** (post-hoc reflection) 机制
- **执行 → 反思 → 优化** 的迭代循环
- 模仿人类的“校对/验算”过程

工作流程
- 执行：生成初稿（如代码）
- 反思：由“评审员”角色分析错误与优化方向
- 优化：根据反馈修正，生成新版本
- 可多轮迭代，直到结果收敛

应用场景
- 代码优化：初稿可能低效，反思后改进为更优算法（如筛法）
- 逻辑推理：发现并修复推理漏洞
- 复杂任务：提升最终结果的质量与可靠性

## 习题

1. 三种范式分析

- 三种范式在“思考”与“行动”的组织方式上有什么本质区别
    - ReAct (Reason + Act)，思想和行动紧密**耦合**，形成**循环**，像人类边想边做，本质是**思考驱动行动，行动反过来修正思考**
    - Plan-and-Solve，先集中思考，规划后再执行，像人类先思考再行动，本质是**思考与行动解耦，思考阶段一次性完成，行动阶段只是执行，不再动态调整**
    - Reflection，先执行，再进行事后反思与优化，像人类写完初稿后再校对、修改，本质是**思考与行动分阶段交替，行动先产出结果，思考在事后进行批判与改进**
- 智能家居控制助手
    - 选ReAct和Reflection
    - 智能家居环境是高度实时的，用户随时可能发出指令（开灯、关窗帘、调节空调）。ReAct 的 思考-行动-观察循环 能够边想边做，快速响应。
    - 每个设备（灯光、空调、窗帘）都可以抽象为一个“工具”。ReAct 能根据用户意图选择合适的工具并立即执行。
    - 如果执行失败（比如设备未响应），ReAct 可以根据观察结果调整策略（重试、换设备、提示用户）。
    - Reflection 可以分析原因并改进，还可以通过事后反思发现规律，并优化策略。
- 三种范式混合的架构
    - Plan-and-Solve：负责全局规划，生成任务蓝图
    - ReAct：在执行阶段，边想边做，动态调用工具
    - Reflection：在任务完成后，进行事后反思与优化
  
2. 思考ReAct
- 当前的解析方法存在哪些潜在的脆弱性？
  - 格式依赖性强，缺乏鲁棒性。正则表达式假定LLM输出严格遵循Thought和Action的固定格式，如果模型的输出中有额外空格、换行、大小写差异或者标点符号，就可能导致匹配失败。
  - 多行内容处理不足。如果Thought或Action的内容跨多行，正则表达式可能只会捕获第一行，导致信息丢失。
  - 歧义或者嵌套情况。如果Action中包含“Action”的字符串，正则表达式可能错误的截取。
  - 错误容忍率低。一旦LLM的输出不符合预期格式，整个流程就会中断了，不会尝试修正或者回退。
- 在什么情况下可能会失败？
  - 模型输出不规范：输出了 `Thought - 我需要搜索... 而不是 Thought:`，输出了 `Action:Search[...]（缺少空格）或 Action = Search[...]`。
  - 跨行输出：Thought: 后面跟着多行推理文本，正则只捕获第一行。
  - 额外解释或注释：模型在输出中加入了说明文字，例如：
    ```
      Thought: 我需要搜索华为最新手机
      （这是我的思考过程）
      Action: Search[华为最新手机]
      ```
  - 工具调用格式变化。模型输出 `Search("华为最新手机") 而不是 Search[华为最新手机]`。
  - 语言或符号差异。模型输出中文标签（如“思考：”而不是“Thought:”），正则无法匹配。
- 改进脆弱性
  - 使用 **更宽松的正则**（允许空格、大小写、换行）。
  - 在提示词中加入 **few-shot** 示例，强化模型输出的格式一致性。例如
    ```
    Question: 华为最新手机是什么？ 
    Thought: 我需要搜索华为最新手机型号。 
    Action: Search[华为最新手机] 
    Observation: Mate 70 是最新型号。
    Thought: 我已经得到答案。 
    Action: Finish[华为最新手机是 Mate 70]
    ```
  - 增加 **健壮的解析器**：先尝试正则，失败时用字符串查找或 JSON 格式化作为兜底。
  - 在 Action 部分强制输出 **结构化格式（如 JSON）**，避免依赖脆弱的文本解析。
- json输出解析和字符串正则表达式输出解析的优缺点
  - json
    - 优点
      - 结构化强：输出是标准化的键值对，解析时只需 json.loads()，不容易出错。
      - 健壮性高：即使内容跨行或包含复杂信息，JSON 依然能完整表示。
      - 可扩展性好：后续要增加字段（比如 confidence、timestamp）很容易，不会破坏原有解析逻辑。
      - 语言无关：JSON 是通用格式，跨语言、跨系统都能解析。
    - 缺点
      - 模型约束难度高：需要在 Prompt 中强制模型输出合法 JSON，否则容易出现缺失引号、额外注释等问题。
      - 解析失败风险：只要 JSON 不合法，json.loads() 就会报错，需要额外兜底逻辑。
      - 冗长：相比简单的 Thought: ... Action: ...，JSON 格式更啰嗦。
  - 字符串正则表达式输出
    - 优点
      - 实现简单：用几行正则就能提取 Thought 和 Action。
      - 灵活性高：可以快速适配不同的输出格式，不需要模型严格遵守 JSON。
      - 对人类可读性好：输出更接近自然语言，调试时直观。
    - 缺点
      - 脆弱性高：依赖模型输出的固定格式，一旦有空格、换行、标点差异就可能匹配失败。
      - 扩展性差：如果要增加字段（比如 confidence），正则需要重新写，容易出错。
      - 多行处理困难：正则默认只匹配单行，跨行内容需要额外处理。
      - 可维护性低：复杂正则难以阅读和维护。
- 增加一个计算工具
  - 先修改了提示词，增加了`你需要根据不同类型的问题调用不同的工具来解决用户的问题`
  - 询问了同一个问题，两次答案如下
    >现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱
    >
    > --- Step 1 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：在2025年，用2万元人民币购买两台国行iPhone 17 Pro最低配版本，还能剩下多少钱。首先，我需要知道iPhone 17 Pro的最低配版本在2025年的国行价格。由于这是假设的未来产品，我需要搜索相关信息。iPhone 17 Pro可能尚未发布，但根据历史趋势，我可以估计其价格。通常，iPhone Pro系列起售价在人民币8000-10000元左右。为了准确，我应该搜索“iPhone 17 Pro 国行价格 2025”或类似关键词。然后，计算两台的总价，并从2万元中减去，得到剩余金额。",
        "action": {
            "type": "tool",
            "name": "GoogleSearch",
            "input": "iPhone 17 Pro 国行价格 2025"
        }
    }
    Thought: 用户的问题是：在2025年，用2万元人民币购买两台国行iPhone 17 Pro最低配版本，还能剩下多少钱。首先，我需要知道iPhone 17 Pro的最低配版本在2025年的国行价格。由于这是假设的未来产品，我需要搜索相关信息。iPhone 17 Pro可能尚未发布，但根据历史趋势，我可以估计其价格。通常，iPhone Pro系列起售价在人民币8000-10000元左右。为了准确，我应该搜索“iPhone 17 Pro 国行价格 2025”或类似关键词。然后，计算两台的总价，并从2万元中减去，得到剩余金额。
    Action: GoogleSearch with input: iPhone 17 Pro 国行价格 2025
    Searching Google for: iPhone 17 Pro 国行价格 2025
    Observation: 苹果 2025 秋季新品发布会结束，iPhone 17 系列国行价格正式公布，标准版 5999 元起，Pro Max 顶配高达 17999 元。 #iPhone17价格# #苹果发布会#
    >
    > --- Step 2 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:action: tool\n\nObservation: 苹果 2025 秋季新品发布会结束，iPhone 17 系列国行价格正式公布，标准版 5999 元起，Pro Max 顶配高达 17999 元。 #iPhone17价格# #苹果发布会#\n\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：在2025年，用2万元人民币购买两台国行iPhone 17 Pro最低配版本，还能剩下多少钱。我需要知道iPhone 17 Pro最低配版本的具体价格。从历史观察中，我看到一条关于iPhone 17系列国行价格的信息，但只提到了标准版起价5999元，Pro Max顶配17999元，没有明确提到iPhone 17 Pro的价格。因此，我需要搜索更详细的信息来获取iPhone 17 Pro最低配版本的确切价格。",
        "action": {
            "type": "tool",
            "name": "GoogleSearch",
            "input": "iPhone 17 Pro 国行价格 最低配 2025"
        }
    }
    Thought: 用户的问题是：在2025年，用2万元人民币购买两台国行iPhone 17 Pro最低配版本，还能剩下多少钱。我需要知道iPhone 17 Pro最低配版本的具体价格。从历史观察中，我看到一条关于iPhone 17系列国行价格的信息，但只提到了标准版起价5999元，Pro Max顶配17999元，没有明确提到iPhone 17 Pro的价格。因此，我需要搜索更详细的信息来获取iPhone 17 Pro最低配版本的确切价格。
    Action: GoogleSearch with input: iPhone 17 Pro 国行价格 最低配 2025
    Searching Google for: iPhone 17 Pro 国行价格 最低配 2025
    Observation: 9月10日凌晨消息，今日，苹果2025年秋季发布会在美国加州库比蒂诺的苹果园区 (Apple Park)的史蒂夫·乔布斯剧院举行，此次发布会主题为“Awe Dropping”（前方超燃）。 会上，苹果iPhone 17 Pro及iPhone 17 Pro Max正式发布，新机型全线256GB 存储容量起，并首次推出2TB的配置。 价格方面，iPhone 17 Pro系列起售价为1099美元。 国行版价格，iPhone 17 Pro售价8999元起，iPhone 17 Pro max 售价9999元起。 外观方面，iPhone 17 Pro系列提供橙色、深蓝色等三款配色。
    >
    > --- Step 3 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:action: tool\n\nObservation: 苹果 2025 秋季新品发布会结束，iPhone 17 系列国行价格正式公布，标准版 5999 元起，Pro Max 顶配高达 17999 元。 #iPhone17价格# #苹果发布会#\n\naction: tool\n\nObservation: 9月10日凌晨消息，今日，苹果2025年秋季发布会在美国加州库比蒂诺的苹果园区 (Apple Park)的史蒂夫·乔布斯剧院举行，此次发布会主题为“Awe Dropping”（前方超燃）。 会上，苹果iPhone 17 Pro及iPhone 17 Pro Max正式发布，新机型全线256GB 存储容量起，并首次推出2TB的配置。 价格方面，iPhone 17 Pro系列起售价为1099美元。 国行版价格，iPhone 17 Pro售价8999元起，iPhone 17 Pro max 售价9999元起。 外观方面，iPhone 17 Pro系列提供橙色、深蓝色等三款配色。\n\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。从历史记录中，我已经通过搜索工具获取了相关信息。历史记录显示：iPhone 17 Pro国行版起售价为8999元。用户想买两台最低配版本，所以总价是8999 * 2 = 17998元。用户有2万元，所以剩余金额是20000 - 17998 = 2元。这个计算很简单，不需要再搜索价格信息了，因为历史记录中已经给出了明确的价格。我可以直接使用计算器来确认这个减法计算。",
        "action": {
            "type": "tool",
            "name": "Calculator",
            "input": "20000 - 8999 * 2"
        }
    }
    Thought: 用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。从历史记录中，我已经通过搜索工具获取了相关信息。历史记录显示：iPhone 17 Pro国行版起售价为8999元。用户想买两台最低配版本，所以总价是8999 * 2 = 17998元。用户有2万元，所以剩余金额是20000 - 17998 = 2元。这个计算很简单，不需要再搜索价格信息了，因为历史记录中已经给出了明确的价格。我可以直接使用计算器来确认这个减法计算。
    Action: Calculator with input: 20000 - 8999 * 2
    Observation: 2002
    >
    > --- Step 4 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:action: tool\n\nObservation: 苹果 2025 秋季新品发布会结束，iPhone 17 系列国行价格正式公布，标准版 5999 元起，Pro Max 顶配高达 17999 元。 #iPhone17价格# #苹果发布会#\n\naction: tool\n\nObservation: 9月10日凌晨消息，今日，苹果2025年秋季发布会在美国加州库比蒂诺的苹果园区 (Apple Park)的史蒂夫·乔布斯剧院举行，此次发布会主题为“Awe Dropping”（前方超燃）。 会上，苹果iPhone 17 Pro及iPhone 17 Pro Max正式发布，新机型全线256GB 存储容量起，并首次推出2TB的配置。 价格方面，iPhone 17 Pro系列起售价为1099美元。 国行版价格，iPhone 17 Pro售价8999元起，iPhone 17 Pro max 售价9999元起。 外观方面，iPhone 17 Pro系列提供橙色、深蓝色等三款配色。\n\naction: tool\n\nObservation: 2002\n\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史记录中的观察信息，iPhone 17 Pro国行版起售价为8999元。我需要计算购买两台iPhone 17 Pro最低配版本的总花费，然后用2万元减去这个总花费，得到剩余的钱。首先，计算总花费：8999元/台 * 2台 = 17998元。然后，计算剩余：20000元 - 17998元 = 2元。为了确保计算准确，我可以使用Calculator工具进行验证。",
        "action": {
            "type": "tool",
            "name": "Calculator",
            "input": "20000 - 8999 * 2"
        }
    }
    Thought: 用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史记录中的观察信息，iPhone 17 Pro国行版起售价为8999元。我需要计算购买两台iPhone 17 Pro最低配版本的总花费，然后用2万元减去这个总花费，得到剩余的钱。首先，计算总花费：8999元/台 * 2台 = 17998元。然后，计算剩余：20000元 - 17998元 = 2元。为了确保计算准确，我可以使用Calculator工具进行验证。
    Action: Calculator with input: 20000 - 8999 * 2
    Observation: 2002
    >
    > --- Step 5 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:action: tool\n\nObservation: 苹果 2025 秋季新品发布会结束，iPhone 17 系列国行价格正式公布，标准版 5999 元起，Pro Max 顶配高达 17999 元。 #iPhone17价格# #苹果发布会#\n\naction: tool\n\nObservation: 9月10日凌晨消息，今日，苹果2025年秋季发布会在美国加州库比蒂诺的苹果园区 (Apple Park)的史蒂夫·乔布斯剧院举行，此次发布会主题为“Awe Dropping”（前方超燃）。 会上，苹果iPhone 17 Pro及iPhone 17 Pro Max正式发布，新机型全线256GB 存储容量起，并首次推出2TB的配置。 价格方面，iPhone 17 Pro系列起售价为1099美元。 国行版价格，iPhone 17 Pro售价8999元起，iPhone 17 Pro max 售价9999元起。 外观方面，iPhone 17 Pro系列提供橙色、深蓝色等三款配色。\n\naction: tool\n\nObservation: 2002\n\naction: tool\n\nObservation: 2002\n\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史观察，iPhone 17 Pro国行版起售价为8999元。我需要计算购买两台iPhone 17 Pro最低配版本的总花费，然后用20000元减去这个总花费，得到剩余金额。首先，计算总花费：8999元/台 * 2台 = 17998元。然后，计算剩余金额：20000元 - 17998元 = 2元。因此，剩余金额为2元。",
        "action": {
            "type": "finish",
            "answer": "购买两台国行iPhone 17 Pro最低配版本（每台8999元）的总花费为17998元。使用2万元人民币购买后，还能剩下2元。"
        }
    }
    Thought: 用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史观察，iPhone 17 Pro国行版起售价为8999元。我需要计算购买两台iPhone 17 Pro最低配版本的总花费，然后用20000元减去这个总花费，得到剩余金额。首先，计算总花费：8999元/台 * 2台 = 17998元。然后，计算剩余金额：20000元 - 17998元 = 2元。因此，剩余金额为2元。
    Final Answer: 购买两台国行iPhone 17 Pro最低配版本（每台8999元）的总花费为17998元。使用2万元人民币购买后，还能剩下2元。
    root@DESKTOP-MV4G0KD:/opt/hello-agent/code/chapterfour/agents_demo# poetry run python -m react_demo.ReAct
    Registered tool: GoogleSearch successfully.
    Registered tool: Calculator successfully.
    Please enter your question: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱
    >
    > --- Step 1 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：现在是2025年，iPhone 17 Pro系列已经发布，用2万元人民币购买两台国行iPhone 17 Pro最低配版本，还能剩下多少钱？要回答这个问题，我需要知道iPhone 17 Pro国行最低配版本的价格。由于这是2025年的产品，我需要搜索当前（2025年）iPhone 17 Pro的官方售价或市场价。然后计算两台的总价，再用2万元减去总价得到剩余金额。",
        "action": {
            "type": "tool",
            "name": "GoogleSearch",
            "input": "2025年 iPhone 17 Pro 国行 最低配 价格"
        }
    }
    Thought: 用户的问题是：现在是2025年，iPhone 17 Pro系列已经发布，用2万元人民币购买两台国行iPhone 17 Pro最低配版本，还能剩下多少钱？要回答这个问题，我需要知道iPhone 17 Pro国行最低配版本的价格。由于这是2025年的产品，我需要搜索当前（2025年）iPhone 17 Pro的官方售价或市场价。然后计算两台的总价，再用2万元减去总价得到剩余金额。
    Action: GoogleSearch with input: 2025年 iPhone 17 Pro 国行 最低配 价格
    Searching Google for: 2025年 iPhone 17 Pro 国行 最低配 价格
    Observation: iPhone 17标准版5999元起，256GB版本同价且支持国补，512GB版本7999元起；iPhone Air售价7999元起，256GB版本同价，512GB版本9999元起，1TB版本11999元起；iPhone 17 Pro售价8999元起，256GB版本同价，512GB版本10999元起，1TB版本12999元起；iPhone 17 Pro Max的256GB版本9999元起，512GB版本11999元起，1TB版本13999元起，2TB版本17999元起。 (AI生成)
    >
    > --- Step 2 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:action: tool\n\nObservation: iPhone 17标准版5999元起，256GB版本同价且支持国补，512GB版本7999元起；iPhone Air售价7999元起，256GB版本同价，512GB版本9999元起，1TB版本11999元起；iPhone 17 Pro售价8999元起，256GB版本同价，512GB版本10999元起，1TB版本12999元起；iPhone 17 Pro Max的256GB版本9999元起，512GB版本11999元起，1TB版本13999元起，2TB版本17999元起。 (AI生成)\n\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：在2025年，用2万元人民币购买两台国行iPhone 17 Pro最低配版本，还能剩下多少钱。根据历史观察，iPhone 17 Pro的起售价是8999元，这是256GB版本的价格，应该就是最低配版本。所以，两台iPhone 17 Pro的最低配总价是8999元 * 2 = 17998元。然后，用20000元减去17998元，就能得到剩余的钱。这需要计算，所以使用Calculator工具。",
        "action": {
            "type": "tool",
            "name": "Calculator",
            "input": "20000 - 8999 * 2"
        }
    }
    Thought: 用户的问题是：在2025年，用2万元人民币购买两台国行iPhone 17 Pro最低配版本，还能剩下多少钱。根据历史观察，iPhone 17 Pro的起售价是8999元，这是256GB版本的价格，应该就是最低配版本。所以，两台iPhone 17 Pro的最低配总价是8999元 * 2 = 17998元。然后，用20000元减去17998元，就能得到剩余的钱。这需要计算，所以使用Calculator工具。
    Action: Calculator with input: 20000 - 8999 * 2
    Observation: 2002
    >
    > --- Step 3 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:action: tool\n\nObservation: iPhone 17标准版5999元起，256GB版本同价且支持国补，512GB版本7999元起；iPhone Air售价7999元起，256GB版本同价，512GB版本9999元起，1TB版本11999元起；iPhone 17 Pro售价8999元起，256GB版本同价，512GB版本10999元起，1TB版本12999元起；iPhone 17 Pro Max的256GB版本9999元起，512GB版本11999元起，1TB版本13999元起，2TB版本17999元起。 (AI生成)\n\naction: tool\n\nObservation: 2002\n\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史信息，iPhone 17 Pro的最低配版本（起售价）是8999元。我需要计算购买两台的总花费，然后从2万元中减去这个总花费，得到剩余金额。首先，计算两台iPhone 17 Pro最低配的总价：8999元 * 2 = 17998元。然后，计算剩余金额：20000元 - 17998元 = 2元。但历史观察中有一个'2002'，这可能是一个无关信息或错误。为了确保准确性，我应该重新确认iPhone 17 Pro的最低配价格。历史信息显示：'iPhone 17 Pro售价8999元起，256GB版本同价'，这意味着最低配（可能是128GB或256GB？）是8999元起。但用户提到'最低配版本'，所以应该是8999元的版本。因此，总价17998元，剩余2元。但为了更严谨，我可以使用计算器工具来验证计算。",
        "action": {
            "type": "tool",
            "name": "Calculator",
            "input": "20000 - 8999 * 2"
        }
    }
    Thought: 用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史信息，iPhone 17 Pro的最低配版本（起售价）是8999元。我需要计算购买两台的总花费，然后从2万元中减去这个总花费，得到剩余金额。首先，计算两台iPhone 17 Pro最低配的总价：8999元 * 2 = 17998元。然后，计算剩余金额：20000元 - 17998元 = 2元。但历史观察中有一个'2002'，这可能是一个无关信息或错误。为了确保准确性，我应该重新确认iPhone 17 Pro的最低配价格。历史信息显示：'iPhone 17 Pro售价8999元起，256GB版本同价'，这意味着最低配（可能是128GB或256GB？）是8999元起。但用户提到'最低配版本'，所以应该是8999元的版本。因此，总价17998元，剩余2元。但为了更严谨，我可以使用计算器工具来验证计算。
    Action: Calculator with input: 20000 - 8999 * 2
    Observation: 2002
    >
    > --- Step 4 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:action: tool\n\nObservation: iPhone 17标准版5999元起，256GB版本同价且支持国补，512GB版本7999元起；iPhone Air售价7999元起，256GB版本同价，512GB版本9999元起，1TB版本11999元起；iPhone 17 Pro售价8999元起，256GB版本同价，512GB版本10999元起，1TB版本12999元起；iPhone 17 Pro Max的256GB版本9999元起，512GB版本11999元起，1TB版本13999元起，2TB版本17999元起。 (AI生成)\n\naction: tool\n\nObservation: 2002\n\naction: tool\n\nObservation: 2002\n\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史记录中的观察，iPhone 17 Pro的最低配版本（256GB）售价为8999元起。我需要计算购买两台的总价，然后从2万元中减去这个总价，得到剩余金额。首先，计算两台iPhone 17 Pro 256GB的总价：8999元 * 2 = 17998元。然后，计算剩余金额：20000元 - 17998元 = 2元。但为了确保准确性，我应该使用计算器进行验证。",
        "action": {
            "type": "tool",
            "name": "Calculator",
            "input": "20000 - 8999 * 2"
        }
    }
    Thought: 用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史记录中的观察，iPhone 17 Pro的最低配版本（256GB）售价为8999元起。我需要计算购买两台的总价，然后从2万元中减去这个总价，得到剩余金额。首先，计算两台iPhone 17 Pro 256GB的总价：8999元 * 2 = 17998元。然后，计算剩余金额：20000元 - 17998元 = 2元。但为了确保准确性，我应该使用计算器进行验证。
    Action: Calculator with input: 20000 - 8999 * 2
    Observation: 2002
    >
    > --- Step 5 ---
    Calling model: deepseek-chat with messages: [{'role': 'user', 'content': '\n你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。\n\n以下是你可以使用的工具：\nGoogleSearch: Use this tool to search Google for information.\nCalculator: Simple calculator implemention.\n\n当你收到一个用户的问题时，按照json格式进行回应：\n\n{\n    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",\n    "action": {\n        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",\n        "name": "当type=tool时填写工具名称，例如Search",\n        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",\n        "answer": "当type=finish时填写最终答案",\n    }\n}\n说明\n- 如果你使用一个工具，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "tool",\n        "name": "{tool_name}",\n        "input": "{tool_input}",\n    }\n}\n- 如果你的信息足以回答问题，请输出：\n{\n    "thought": "...",\n    "action":{\n        "type": "finish",\n        "answer": "最终答案",   \n    }\n}\n\n现在，开始解决以下问题:\nQuestion: 现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱\nHistory:action: tool\n\nObservation: iPhone 17标准版5999元起，256GB版本同价且支持国补，512GB版本7999元起；iPhone Air售价7999元起，256GB版本同价，512GB版本9999元起，1TB版本11999元起；iPhone 17 Pro售价8999元起，256GB版本同价，512GB版本10999元起，1TB版本12999元起；iPhone 17 Pro Max的256GB版本9999元起，512GB版本11999元起，1TB版本13999元起，2TB版本17999元起。 (AI生成)\n\naction: tool\n\nObservation: 2002\n\naction: tool\n\nObservation: 2002\n\naction: tool\n\nObservation: 2002\n\n'}]
    Receiving streamed response:
    {
        "thought": "用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史记录中的观察，iPhone 17 Pro的起售价是8999元，这是最低配版本的价格。我需要计算购买两台iPhone 17 Pro最低配版本的总花费，然后用2万元减去这个总花费，得到剩余的钱。计算过程是：总花费 = 8999 * 2 = 17998元。剩余 = 20000 - 17998 = 2002元。历史记录中已经多次观察到2002，这验证了计算结果。因此，我有足够的信息回答用户的问题。",
        "action": {
            "type": "finish",
            "answer": "购买两台国行iPhone 17 Pro最低配版本（每台8999元）的总花费是17998元。使用2万元人民币购买后，还能剩下2002元。"
        }
    }
    Thought: 用户的问题是：现在是2025年，iPhone17系列已经发布，如果我使用2万元人民币购买两台国行iPhone 17pro最低配版本，还能剩下多少钱。根据历史记录中的观察，iPhone 17 Pro的起售价是8999元，这是最低配版本的价格。我需要计算购买两台iPhone 17 Pro最低配版本的总花费，然后用2万元减去这个总花费，得到剩余的钱。计算过程是：总花费 = 8999 * 2 = 17998元。剩余 = 20000 - 17998 = 2002元。历史记录中已经多次观察到2002，这验证了计算结果。因此，我有足够的信息回答用户的问题。
    Final Answer: 购买两台国行iPhone 17 Pro最低配版本（每台8999元）的总花费是17998元。使用2万元人民币购买后，还能剩下2002元。

 - 设计并实现一个"工具选择失败"的处理机制
   - 为每个任务维护一个 **错误计数器**
   - 如果错误次数超过阈值（如 3 次），触发纠错机制
   - 当错误次数达到阈值时，给模型一个纠错提示
   - 如果模型仍然无法纠正：回退到默认工具或者直接返回给用户错误信息。
 - 当前调用工具的局限性
   - 提示词冗长：几十个工具的描述会让 Prompt 变得非常长，模型解析成本高，容易出现幻觉或忽略部分工具。
   - 检索效率低：模型在生成 Action 时需要在大量工具中选择，容易选错或混淆。
   - 维护困难：工具描述更新或新增时，需要手动修改 Prompt，容易出错。
 - 当可调用工具数量变多时，如何从工程角度如何优化工具的组织和检索机制
   - 工具分类与分层组织
     - 将工具按功能类别分组，例如：信息检索类、计算类、数据处理类
     - 在 Prompt 中只暴露一级类别，模型先选择类别，再在类别内选择具体工具，类似于“菜单导航”，减少一次性暴露的数量。
   - 工具索引与检索机制
     - 为每个工具建立一个 索引库（例如 JSON 或数据库），包含工具名、描述、示例。
     - 当模型需要选择工具时，先用一个“工具检索器”来匹配最相关的工具，再调用
   - 动态工具注入
     - 不在 Prompt 中一次性列出所有工具，而是根据用户问题动态选择相关工具注入。
   - 工具调用日志与反馈
     - 记录工具调用成功率和失败率，自动调整工具描述的权重。
     - 对常用工具提供更详细的描述和示例，对冷门工具简化描述

- 如何设计一个“动态重规划”机制
  - 失败检测
    - 在执行器中增加**状态检查**：每一步执行后，验证结果是否符合预期
      - 明确界定输出的内容
        - 设置成功条件：用布尔表达式和容差而非主观描述明确什么算“成功”，例如结果必须为 JSON，字段齐全；主键唯一；数值在阈值内；无空值。
        - 设置模式：对每一步输出定义模式（类型、必填、取值范围）。
        - 设置前置/后置条件：步骤前置条件满足，执行后至少满足若干后置条件。
        - 幂等性与副作用：幂等标识、允许的副作用范围（只读/写入路径）。
        - 容差与服务级别协议：明确误差和时延容差，比如“< 200 ms”，“偏差 ≤ 1%”。
      - 验证策略与检查
        - 结构验证：必须是可解析的格式（JSON/YAML/CSV），字段齐全、类型正确、枚举合法。
        - 内容断言：唯一性、非空、单调性、排序正确、键集合匹配、无重复、约束满足。
        - 不变量检查：输入/输出守恒或业务不变量不被破坏（总和一致、计数不增加等）。
        - 跨工具一致性：同一事实用独立方法二次验证（如 API 与本地计算一致）。
        - 差异/影响检查：对状态改变进行差异分析：变更数、范围、越界检测、回滚点可用。
        - 性能与资源检查：运行时间、内存、IO、网络错误率、重试次数在阈值内。
        - 语义验证：文本类用关键词覆盖、正则约束、向量/相似度阈值。
        - 灰度测试：先在小样本或影子环境验证，再推广到完整执行。
        - 基准或参考对比：与基准实现或已知样例对比，误差在可接受范围。
      - 步骤级验证器设计
        - 逐步验证器：每个步骤绑定一个验证器函数，失败则触发重规划。
        - 复合验证：允许多个验证器并行，聚合结果为最终判定。
        - 诊断信息：验证失败返回可操作的错误原因和上下文，用于重规划提示。
        - 审计日志：每次验证记录输入、输出、断言、度量值、结论，便于审计和复盘。
    - 如果结果为空、错误或者与逻辑不符，就触发“失败事件”
  - 反馈通道
    - 将失败信息返回给规划器
    - 反馈当前失败内容，包括：当前失败步骤的描述、错误信息或者异常信息、已完成的历史步骤
  - 局部重规划
    - 规划器不需要完全推翻原计划，只需要基于反馈重新生成后续步骤，这又包含两种策略：
      - **局部替换**：只替换失败的步骤及其依赖链
      - **整体修订**：重新生成完整计划，但保留已经完成的部分
  - 设计提示词：在Plnner中加入“上下文修订”的能力
  - 执行器的迭代控制
    - 执行器需要支持 **Plan → Execute → Re-Plan → Execute** 的循环
    - 设置最大迭代次数，避免陷入无限重规划
- Reflection 机制的终止条件是"反馈中包含无需改进"或"达到最大迭代次数"。这种设计是否合理？
  - **过早终止**：模型可能因为提示词或上下文不足而误判“无需改进”，导致结果仍有缺陷。
  - **过度迭代**：即使结果已经足够好，仍然会继续迭代直到达到上限，浪费算力和时间。
- 设计一个更智能的终止条件
  - 质量阈值判定：在反馈中引入“评分机制”，例如对正确性、效率、可读性分别打分，当综合评分超过设定阈值（如 ≥ 90/100），即可终止。
  - 改进幅度检测：比较前后版本的差异（代码 diff、文本相似度、性能指标）。如果改进幅度低于某个阈值（如性能提升 < 5% 或文本相似度 > 95%），说明迭代已收敛，可以终止。
  - 多评审员一致性：使用多个不同提示词或模型实例作为“评审员”。当多数评审员一致认为“无需改进”时才终止。降低单一模型误判的风险。
  - 任务上下文驱动：根据任务类型动态调整终止条件：
      - 代码优化：性能指标达到预期或复杂度已降至合理范围。
      - 文本生成：逻辑一致性和事实性验证通过。
      - 数据处理：结果满足不变量和约束条件。
  - 用户/外部验证反馈
    - 引入外部验证器（如单元测试、schema 校验、业务规则检查），当验证器通过时即可终止，而不是仅依赖模型的自我反思。
- "客服智能体"
  - 选择框架
  
    | 范式 | 作用 | 优势 | 局限 | 在系统中的定位 |
    | ---- | ---- | ---- | ---- | ---- |
    | Plan-and-Execute | 任务分解与顺序执行 | 可审计、清晰的步骤 | 静态计划易失效 | 作为主流程骨架 |
    | Tool-augmented | 精准使用外部工具 | 数据实时、可控副作用 | 依赖工具质量 | 作为执行器能力层 |
    | Reflection | 质量复核与风险审慎 | 降低误判、优化表达 | 可能过度迭代 | 用于低置信度与有争议案例 |
    | Dynamic Replanning | 失败后的局部修订 | 提升鲁棒性 | 加复杂度与成本 | 处理查询失败、冲突政策等 |
    | Retrieval-augmented（RAG）| 引入公司政策与知识库 | 降低幻觉、统一口径 | 需维护知识质量 | 支撑政策判断与话术一致性 |
  - 工具
    - 订单查询 API：按订单号/邮箱获取订单详情（商品、金额、支付状态、下单与发货时间）。
    - 物流查询 API：查询当前物流状态（揽收、运输、派送、签收、异常）。
    - 政策判定引擎： 将公司政策编码为规则集/条件树，产出判定结果与理由。
    - 知识库检索知识库检索（RAG）：检索最新政策、FAQ、模板话术，辅助生成与核对。
    - 邮件服务： 生成并发送邮件，支持模板与个性化插值。
    - 置信度与争议评估器：结合规则覆盖度、数据完备性、冲突信号，输出置信度与争议标签。
    - 审计与合规日志：全链路记录输入、工具调用、政策依据、决策与邮件正文。
  - 提示词设计
    - 系统角色与原则
      - 角色定位： 你是“客服智能体”，职责是在公司政策框架内，公平、礼貌地处理退款请求。
      - 决策准则：
        - 政策优先： 严格遵循最新政策与规则引擎结果。
        - 证据充分： 只依据查询到的订单与物流数据，不臆测。
        - 风险控制： 低置信度或规则冲突时采取保守策略并升级处理。
        - 用户体验： 保持尊重与同理心，清晰解释决定与后续选项。
        - 可审计： 所有输出必须结构化并附带政策条款编号与数据来源。
    - 决策与结构化输出契约
      - 输出模式： 以 JSON 返回
        - decision: approve/partial/deny/escalate
        - confidence: 0–1
        - policy_refs: [规则ID]
        - evidence: 订单/物流关键字段
        - reasoning: 简洁可解释理由（不含敏感内部信息）
        - email_body: 面向用户的邮件草案
        - next_actions: 升级或用户选项
      - 语言要求：
        - 友好且专业：使用礼貌称呼、感谢与理解性的表达。
        - 明确透明：说明判定依据与可选路径（申诉/补充材料/等待签收等）。
        - 避免承诺超权：作超出政策与权限的承诺。
    - 工具调用指令
      - 订单查询：以订单号/邮箱调用，若数据缺失，返回“需要用户补充信息”。
      - 物流查询：当订单状态需要物流确认时调用；对异常状态进行标注。
      - 政策引擎：输入结构化事实，输出规则匹配结果与条款编号；禁止自由裁量绕过规则。
    - 反思与争议处理
      - 触发条件： confidence < 阈值，或 policy_refs 之间存在冲突，或 evidence 不完整。
      - 反思目标：
        - 覆盖度检查：是否遗漏相关政策或证据？
        - 风险评估：拒绝的潜在客诉风险、批准的成本影响。
      - 停止条件： 质量评分 ≥ 设定阈值，改进幅度 < 最小差异，或达到迭代上限。
    - 风险与挑战，以及技术化缓解手段
      - 数据幻觉与误判：强制工具优先与只读事实；结构化输出契约 + Schema 校验；与政策引擎双轨一致性检查。
      - 政策漂移与不一致：政策版本化与生效期标注；RAG 索引按版本隔离；判定结果必须包含 policy_refs 并在审计中校验。
      - 低置信度与争议案例积压：置信度打分器 + 反思环；人类介入（human-in-the-loop）队列与SLA；主动请求补充材料。
      - 用户体验与品牌风险： 模板化话术 + 个性化插值；语气与用词审查器；A/B 测试与投诉监控闭环。
      - 隐私与合规：最小化数据访问、字段级脱敏；权限分级与审计；邮件域名认证（SPF/DKIM/DMARC），退信与退订管理。
      - 安全与对抗性输：系统提示词硬约束 + 工具白名单；输入净化与指令分离；策略引擎作为最终裁决。
      - 可用性与稳定性：重试与降级策略；动态重规划（改为请求补充或延后响应）；超时与幂等设计。