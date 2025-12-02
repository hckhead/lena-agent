import asyncio
from agent.graph import app
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from dotenv import load_dotenv
import json
import sys

load_dotenv()

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_message(msg, index):
    if isinstance(msg, HumanMessage):
        print(f"[{index}] User: {msg.content}")
    elif isinstance(msg, AIMessage):
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"[{index}] AI (Tool Calls):")
            for tool_call in msg.tool_calls:
                print(f"  Tool: {tool_call['name']}")
                print(f"  Args: {json.dumps(tool_call['args'], ensure_ascii=False, indent=2)}")
        else:
            print(f"[{index}] AI: {msg.content}")
    elif isinstance(msg, ToolMessage):
        content_preview = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
        print(f"[{index}] Tool Result: {content_preview}")

async def test_rag():
    print_separator("TEST 1: RAG (Document Search)")
    print("Query: 'LENA information from internal docs'")
    
    inputs = {"messages": [HumanMessage(content="LENA information from internal docs")]}
    
    message_count = 0
    async for chunk in app.astream(inputs, stream_mode="values"):
        messages = chunk["messages"]
        if len(messages) > message_count:
            for i in range(message_count, len(messages)):
                print_message(messages[i], i)
            message_count = len(messages)
    
    print(f"\nRAG test completed ({message_count} messages)")
    return True

async def test_http():
    print_separator("TEST 2: HTTP Request Tool")
    print("Query: 'Send GET request to httpbin.org/get'")
    
    inputs = {"messages": [HumanMessage(content="Send GET request to httpbin.org/get")]}
    
    message_count = 0
    async for chunk in app.astream(inputs, stream_mode="values"):
        messages = chunk["messages"]
        if len(messages) > message_count:
            for i in range(message_count, len(messages)):
                print_message(messages[i], i)
            message_count = len(messages)
    
    print(f"\nHTTP test completed ({message_count} messages)")
    return True

async def test_tavily():
    print_separator("TEST 3: Tavily Web Search")
    print("Query: 'Search for LENA on docs.lenalab.org'")
    
    inputs = {"messages": [HumanMessage(content="Search for LENA information on docs.lenalab.org")]}
    
    message_count = 0
    async for chunk in app.astream(inputs, stream_mode="values"):
        messages = chunk["messages"]
        if len(messages) > message_count:
            for i in range(message_count, len(messages)):
                print_message(messages[i], i)
            message_count = len(messages)
    
    print(f"\nTavily test completed ({message_count} messages)")
    return True

async def test_context7():
    print_separator("TEST 4: Context7 MCP")
    print("Query: 'Apache configuration using Context7'")
    
    inputs = {"messages": [HumanMessage(content="Tell me about Apache configuration using Context7")]}
    
    message_count = 0
    try:
        async for chunk in app.astream(inputs, stream_mode="values"):
            messages = chunk["messages"]
            if len(messages) > message_count:
                for i in range(message_count, len(messages)):
                    print_message(messages[i], i)
                message_count = len(messages)
        
        print(f"\nContext7 test completed ({message_count} messages)")
        return True
    except Exception as e:
        print(f"\nContext7 test failed: {str(e)}")
        print("(Context7 MCP server may not be running)")
        return False

async def main():
    print("\n" + "="*60)
    print("  LENA Agent Integration Test")
    print("="*60)
    
    results = {
        "RAG": False,
        "HTTP": False,
        "Tavily": False,
        "Context7": False
    }
    
    try:
        results["RAG"] = await test_rag()
        results["HTTP"] = await test_http()
        results["Tavily"] = await test_tavily()
        results["Context7"] = await test_context7()
        
        print_separator("Test Summary")
        for tool, success in results.items():
            status = "PASS" if success else "FAIL"
            print(f"{tool:15} : {status}")
        
        print("\nAll tests completed!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nTest failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set UTF-8 encoding for stdout
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")
    
    asyncio.run(main())
