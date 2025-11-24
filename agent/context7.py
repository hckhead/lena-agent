import subprocess
import json
import os
from langchain_core.tools import tool

# Context7 Configuration
CONTEXT7_COMMAND = "npx"
CONTEXT7_ARGS = ["-y", "@upstash/context7-mcp@latest"]

@tool
def context7_tool(query: str) -> str:
    """
    Uses Context7 MCP to search documentation for Apache, Nginx, and Tomcat.
    
    Args:
        query: The search query.
        
    Returns:
        The search results from Context7.
    """
    try:
        # Since we don't have a persistent MCP client session easily available in this stateless tool,
        # and the user provided a CLI command, we might need to check if the CLI supports one-off commands.
        # However, MCP servers usually run over stdio and wait for JSON-RPC messages.
        # Running a fresh npx instance for every request is slow and might not work if it expects a session.
        
        # BUT, for this environment, let's try to run it as a one-off if possible, 
        # OR we can try to use the `mcp-cli` or similar if available.
        
        # Given the constraints and the user's request to "use context7 mcp internally",
        # and the command provided is for the SERVER, we need a CLIENT.
        
        # Let's try to use a python script to interact with the server process.
        # We will spawn the process, send the 'initialize' request, then 'tools/call' (or resources/read), then exit.
        
        # NOTE: This is a simplified implementation. A real implementation would keep the process alive.
        
        # Construct the command
        cmd = [CONTEXT7_COMMAND] + CONTEXT7_ARGS
        
        # We will use a helper script to interact with the MCP server because handling async stdio in a sync tool is tricky.
        # But here we can just do a quick interaction.
        
        # Wait! The user said "context7 mcp... to answer Q&A". 
        # Context7 likely exposes tools or resources. We need to know WHAT tool to call.
        # Usually it's 'search' or similar.
        # Let's assume there is a 'search' tool or we list tools first.
        
        # For now, to avoid blocking, I will return a message saying we need to implement the persistent client
        # or use a library that handles this.
        
        # Let's try to use `mcp` package's client capabilities if possible.
        # Since I cannot easily verify the `mcp` client usage without docs, I will implement a basic interaction.
        
        return "Context7 integration is partially configured. Please verify the tool name to call (e.g., 'search')."

    except Exception as e:
        return f"Error querying Context7: {str(e)}"

# Redefining the tool to actually do something useful if possible.
# Since I can't easily run the npx command and interact with it in a single tool call reliably without a proper client library,
# I will implement a wrapper that uses `mcp` python client to connect to the stdio process.

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def query_context7(query: str):
    server_params = StdioServerParameters(
        command=CONTEXT7_COMMAND,
        args=CONTEXT7_ARGS,
        env=os.environ
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools to find the search tool
            tools = await session.list_tools()
            search_tool_name = None
            for t in tools.tools:
                if "search" in t.name.lower() or "query" in t.name.lower():
                    search_tool_name = t.name
                    break
            
            if not search_tool_name:
                return f"Could not find a search tool in Context7. Available tools: {[t.name for t in tools.tools]}"
            
            # Call the tool
            result = await session.call_tool(search_tool_name, arguments={"query": query})
            return result.content[0].text

def context7_sync_wrapper(query: str) -> str:
    """Wrapper to run async context7 query in sync tool"""
    try:
        return asyncio.run(query_context7(query))
    except Exception as e:
        return f"Error executing Context7 query: {str(e)}"

@tool
def context7_tool(query: str) -> str:
    """
    Uses Context7 MCP to search documentation for Apache, Nginx, and Tomcat.
    
    Args:
        query: The search query.
        
    Returns:
        The search results from Context7.
    """
    return context7_sync_wrapper(query)
