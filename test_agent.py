import asyncio
from agent.graph import app
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("--- Testing RAG ---")
    inputs = {"messages": [HumanMessage(content="How do I deploy Project X?")]}
    async for chunk in app.astream(inputs, stream_mode="values"):
        last_msg = chunk["messages"][-1]
        print(f"Last Message: {last_msg.content}")

    print("\n--- Testing HTTP Tool ---")
    inputs = {"messages": [HumanMessage(content="Check the status of google.com (GET request)")]}
    async for chunk in app.astream(inputs, stream_mode="values"):
        last_msg = chunk["messages"][-1]
        print(f"Last Message: {last_msg.content}")

    print("\n--- Testing Tavily Search ---")
    inputs = {"messages": [HumanMessage(content="LENA에 대해서 알려줘")]}
    async for chunk in app.astream(inputs, stream_mode="values"):
        last_msg = chunk["messages"][-1]
        print(f"Last Message: {last_msg.content}")

    print("\n--- Testing Context7 ---")
    inputs = {"messages": [HumanMessage(content="Apache HTTPD 설정 방법에 대해 알려줘 (Context7 사용)")]}
    async for chunk in app.astream(inputs, stream_mode="values"):
        last_msg = chunk["messages"][-1]
        print(f"Last Message: {last_msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
