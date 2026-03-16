import requests
from bs4 import BeautifulSoup
# ... 你的 fetch_webpage_text 函数 ...

def run_lobster_copilot(url: str):
    # 1. 抓取网页
    raw_text = fetch_webpage_text(url)
    
    # 2. 组装 System Prompt (就是你规定的 JSON 协议和 Markdown 格式)
    system_prompt = "你是一个币安活动解析副驾，请严格按照以下 JSON 和 Markdown 格式输出..."
    
    # 3. 调用 LLM (这里写一段调用大模型的伪代码或真实代码)
    # response = llm.generate(system_prompt + raw_text)
    
    # 4. 返回双重结果
    # return response
