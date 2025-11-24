from mcp.server.fastmcp import FastMCP
from agent.graph import app
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("LENA Agent")

@mcp.tool()
async def ask_agent(query: str) -> str:
    """
    Asks the LangGraph agent a question. The agent has access to documentation (RAG) and HTTP tools.
    
    Args:
        query: The question or command for the agent.
        
    Returns:
        The agent's final response.
    """
    inputs = {"messages": [HumanMessage(content=query)]}
    result = await app.ainvoke(inputs)
    return result["messages"][-1].content

if __name__ == "__main__":
    mcp.run()
