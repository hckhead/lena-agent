from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langgraph.prebuilt import ToolNode
from .state import AgentState
from .rag import get_retriever
from .tools import http_request_tool, tavily_search_tool
from .context7 import context7_tool
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

SYSTEM_PROMPT = """You are a helpful assistant with access to RAG, HTTP tools, and web search.

**Capabilities:**
1.  **RAG**: Answer questions using the provided documentation.
2.  **HTTP Requests**: Execute HTTP requests.
    *   **LENA REST API**: You have access to the LENA REST API. Refer to the API Specification below for available endpoints.
    *   **Authentication**: The system will AUTOMATICALLY inject the API key (`?key=...`) for requests to the LENA API Base URL. You do NOT need to add it manually.
    *   **Swagger/API Usage**: If the user provides Swagger UI information or API documentation, use it to construct the correct HTTP request.
3.  **Web Search**: Use Tavily to search `docs.lenalab.org` and `solution.lgcns.com` for LENA and other solution related queries.
4.  **Context7**: Use the `context7_tool` to access Apache, Nginx, and Tomcat documentation.

**Instructions:**
*   Always prioritize using the provided tools over your internal knowledge.
*   When performing HTTP requests, be precise with URLs, methods, and headers.
*   If the user asks about LENA or LG CNS solutions, use the Tavily search tool.
"""

# Load LENA API Spec
try:
    with open("config/lena_api_spec.md", "r", encoding="utf-8") as f:
        api_spec = f.read()
        SYSTEM_PROMPT += f"\n\n**LENA API Specification:**\n{api_spec}"
except FileNotFoundError:
    pass

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Initialize Tools
tools = [http_request_tool, tavily_search_tool, context7_tool]

# Initialize RAG
retriever = get_retriever()
if retriever:
    def retrieve_docs(query: str) -> str:
        docs = retriever.invoke(query)
        return "\n\n".join([d.page_content for d in docs])

    retriever_tool = Tool(
        name="search_documents",
        func=retrieve_docs,
        description="Searches and returns excerpts from the documentation."
    )
    tools.append(retriever_tool)

# Bind tools to LLM
model = llm.bind_tools(tools)

# Define Nodes
def agent(state: AgentState):
    messages = state['messages']
    # Prepend system prompt if it's not already there (or handled by ChatPromptTemplate)
    # For simplicity in this graph, we can just prepend it to the messages sent to the model
    # or use a prompt template. Let's use a prompt template approach effectively by inserting it.
    
    from langchain_core.messages import SystemMessage
    
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = model.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Define Graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

app = workflow.compile()
