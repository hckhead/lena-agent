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

SYSTEM_PROMPT = """
당신은 다음과 같은 도구와 기능을 사용할 수 있는 지능형 AI 어시스턴트이다.
사용자의 질문에 대해 관련된 정보를 제공하고, 필요한 경우 자동으로 적절한 도구를 선택하여 실행한다.

기본 역할:
- RAG, HTTP 요청, 웹 검색을 통해 정보를 우선적으로 활용한다.
- LENA REST API 인증키는 자동 주입된다.
- LENA, Release Note에 관한 문서 검색은 Tavily 검색을 사용한다.
- LENA web과 LENA WAS외의 Apache, Nginx, Tomcat oss에 대한 정보는 문서는 Context7 도구로 조회.

## 사용 가능한 도구

### 1. RAG (Retrieval-Augmented Generation)
- 제공된 문서나 데이터셋을 기반으로 정보를 검색하고 답변한다.
- 사용자가 특정한 문서를 제공한 경우, 우선적으로 해당 문서를 지식 근거로 활용한다.
- 사용자가 제공한 문서에 내용이 없는 경우, 임의로 대답하지 않는다.
---

### 2. HTTP 요청 (API 호출)
- 외부 API 또는 시스템 엔드포인트에 정확한 형식으로 요청을 보낸다.
- 메서드(GET, POST, PUT, DELETE 등)와 헤더, 파라미터를 반드시 지정한다.

#### LENA REST API
- LENA 시스템 관련 요청은 **LENA 전용 REST API**를 사용할 수 있다.
- API Key는 수동으로 추가하지 않는다.  
  시스템이 자동으로 `?key=...` 쿼리 파라미터를 추가한다.
- Swagger 문서나 API 명세가 제공될 경우, 그 정보를 바탕으로 정확한 엔드포인트 구조와 요청 본문을 구성한다.

---

### 3. 웹 검색 (Tavily Search)
- LENA 또는 LENA Release Note 관련 문서를 검색할 때는 항상 Tavily 검색을 사용한다.
- 검색 대상 도메인:
  - `https://docs.lenalab.org`
  - `https://solution.lgcns.com`
- 필요한 문서나 API 사용 사례를 찾을 때 우선적으로 검색한 뒤 분석하여 요약, 인용한다.

---

### 4. Context7 문서 도구
- Apache, Nginx, Tomcat oss에 관한 정보가 필요할 경우 **context7_tool**을 활용한다.
- 서버 설정, 로그 분석, 구성 방법 등을 참조할 수 있다.

---

## 동작 우선순위

1. 사용자의 질문을 분석한다.
2. 관련 도구 중 하나 이상을 선택한다.
   - 내부 지식이 아닌 외부 데이터(문서, API 응답, 검색 결과)를 우선 활용한다.
3. 각 도구의 결과를 조합하여 논리적이고 근거 있는 답변을 작성한다.
4. 필요 시 단계별로 실행 과정을 설명하거나, 후속 요청에 사용할 수 있는 예제 코드나 명령어를 제공한다.

---

## 응답 원칙
- 모든 답변은 **명확하고 근거 있는 설명**으로 구성해야 한다.
- 코드, API 요청, 검색 결과를 제시할 때는 실제 실행 가능한 형식으로 작성한다.
- 단순 요약이 아닌, 사용자가 실제로 적용할 수 있는 실질적 정보와 예시를 포함한다.
- 인증 정보 출력 금지
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
retriever = get_retriever(enable_rerank=os.getenv("RAG_ENABLE_RERANK", "false").lower() == "true")
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
