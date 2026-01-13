from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from state import SearchState
from node import understand_query_node, tavaily_search_node, generate_answer_node

def create_search_assistant_graph() -> StateGraph:
    """创建一个用于搜索和回答用户查询的状态图"""
    workflow = StateGraph(SearchState)

    # 添加节点
    workflow.add_node("understand", understand_query_node)
    workflow.add_node("search", tavaily_search_node)
    workflow.add_node("answer", generate_answer_node)

    # 设置线性流程
    workflow.add_edge(START, "understand")
    workflow.add_edge("understand", "search")
    workflow.add_edge("search", "answer")
    workflow.add_edge("answer", END)

    # 编译图
    memory = InMemorySaver()
    graph = workflow.compile(checkpointer=memory)

    return graph

if __name__ == "__main__":
    graph = create_search_assistant_graph()

    # 示例运行
    initial_state = SearchState(messages=[{"role": "user", "content": "请帮我查找关于量子计算的最新进展。"}])
    final_state = graph.invoke(initial_state, 
                               {"configurable": {"thread_id": "1"}})
    print("最终回答：", final_state.get("final_answer", "无回答"))