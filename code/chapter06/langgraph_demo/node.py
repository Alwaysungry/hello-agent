from state import SearchState
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from tavily import TavilyClient

import os

load_dotenv()

llm = ChatDeepSeek(
    model = os.getenv("LLM_MODEL"),
    api_key = os.getenv("LLM_API_KEY"),
    base_url = os.getenv("LLM_BASE_URL"),
    temperature = 0.7,
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def understand_query_node(state: SearchState) -> dict:
    """理解用户查询并生成搜索关键词"""
    user_message = state['messages'][-1].content

    understand_prompt = f"""分析用户的查询："{user_message}"
    请完成两个任务：
    1. 简洁总结用户想要了解什么
    2. 生成适合搜索引擎使用的关键词（中英文均可，但是要精准）
    3. 如果用户的查询过于宽泛，请生成多个关键词以覆盖不同方面

    格式：
    理解：[用户需求总结]
    搜索词：[最佳搜索关键词1;最佳搜索关键词2;...]
    """

    response = llm.invoke([SystemMessage(content=understand_prompt)])
    response_text = response.content

    # 解析LLM的输出，提取搜索关键词
    search_query = user_message # 默认使用原始查询
    if "搜索词：" in response_text:
        search_query = response_text.split("搜索词：")[1].strip()
    
    return {
        "user_query": response_text,
        "search_query": search_query,
        "step": "understood",
        "messages": [AIMessage(content=f"我将为您搜索：{search_query}")]
    }

def tavaily_search_node(state: SearchState) -> dict:
    """使用Tavily进行搜索并返回结果"""
    search_query = state['search_query']
    search_results = ""
    try:
        for quuery in search_query.split(";"):
            print(f"正在使用Tavily搜索：{quuery}")
            response = tavily_client.search(query=quuery, search_depth="basic", max_results=5, include_answer=True)

            results = response.get("answer", "未找到相关信息。")
            search_results += results + "\n"

        return {
            "search_results": search_results,
            "step": "searched",
            "messages": [AIMessage(content=f"我找到了以下信息：{search_results}")]
        }
    except Exception as e:
        print(f"搜索时出错：{e}")
        return {
            "search_results": "搜索时出现错误。",
            "step": "searched",
            "messages": [AIMessage(content="抱歉，搜索时出现了问题。")]
        }
    
def generate_answer_node(state: SearchState) -> dict:
    """根据搜索结果生成最终答案"""
    if state["step"] == "search_failed":
        fallback_prompt = f"""由于搜索未能成功，请基于你的知识回答用户的问题。"""
        response = llm.invoke([SystemMessage(content=fallback_prompt)])
    else:
        answer_prompt = f"""基于以下搜索结果，回答用户的查询：
用户查询：\n{state['user_query']}
搜索结果：\n{state['search_results']}
请综合搜索结果，提供准确且有用的回答。请注意，现在的时间是2026年。
"""
        response = llm.invoke([SystemMessage(content=answer_prompt)])
    
    return {
        "final_answer": response.content,
        "step": "answered",
        "messages": [AIMessage(content=response.content)]
    }