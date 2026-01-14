import os

from serpapi import GoogleSearch
# from dotenv import load_dotenv

# load_dotenv()

def search_google(query: str) -> str:
    """
    Perform a Google search using SerpApi and return the results.

    Args:
        query (str): The search query.
    Returns:
        dict: The search results from SerpApi.
    """
    print (f"Searching Google for: {query}")

    try:
        api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            raise ValueError("SERP_API_KEY environment variable not set.")
        parameters = {
            "engine": "bing",
            "q": query,
            "api_key": api_key,
            "gl": "cn",
            "hl": "zn-cn",
        }

        client = GoogleSearch(parameters)
        results = client.get_dict()

        # print (f"Search results received: {results}")
        
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results:
            return results["answer_box"].get("snippet", "No direct answer found.")
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            snippets =[
                f"{idx+1}. {item.get('title', '')}\n{item.get('snippet', '')}"
                for idx, item in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        return "No relevant information found in search results."
    except Exception as e:
        print(f"An error occurred while searching Google: {e}")
        return {}
    
import math

def calculator(expression: str) -> str:
    try:
        # 只允许安全的 eval，避免注入风险
        result = eval(expression, {"__builtins__": None}, {"math": math})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"
    
if __name__ == "__main__":
    # query = "What is the capital of France?"
    # print(search_google(query))

    question = "math.sqrt(16)"
    print(calculator(question))