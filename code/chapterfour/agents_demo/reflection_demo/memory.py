from typing import List, Dict, Any, Optional

class Memory:
    """
    一个简短的记忆模块，用于存储智能体的行动与反思轨迹
    """
    
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
    
    def add_record(self, record_type: str, content: str):
        """
        向记忆中添加一条新记录
        
        param:
        - param record_type: 记录类型
        - param content: 记录内容
        """
        record = {"type": record_type, "content": content}
        self.records.append(record)
        print(f"Update a new record: {record_type}")

    def get_trajectory(self) -> str:
        """
        将所有记忆的记录格式化为一个连贯的字符串文本，用于构建提示词
        """

        trajectory = []

        for record in self.records:
            if record['type'] == 'execution':
                trajectory.append(f"---上一轮尝试---\n{record['content']}")
            elif record['type'] == 'reflection':
                trajectory.append(f"---评审员反馈---\n{record['content']}")

        return "\n\n".join(trajectory)
    
    def get_last_execution(self) -> Optional[str]:
        """
        获取最后一次的执行结果（例如，最新生成的代码）
        如果不存在，返回None
        """

        for record in self.records:
            if record['type'] == 'execution':
                return record['content']
            return None