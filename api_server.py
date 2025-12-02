from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent.graph import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uvicorn
from dotenv import load_dotenv
import time

load_dotenv()

# Initialize FastAPI
api = FastAPI(
    title="LENA Agent API",
    description="OpenAI-compatible API for LENA Agent",
    version="1.0.0"
)

# Enable CORS
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models (OpenAI-compatible)
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "lena-agent"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict

@api.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "LENA Agent API",
        "version": "1.0.0"
    }

@api.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "lena-agent",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "lena"
            }
        ]
    }

@api.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    
    Example request:
    {
        "messages": [
            {"role": "user", "content": "LENA에 대해 알려줘"}
        ]
    }
    """
    try:
        # Convert request messages to LangChain format
        lc_messages = []
        for msg in request.messages:
            if msg.role == "system":
                lc_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
        
        # Invoke the agent
        inputs = {"messages": lc_messages}
        result = await agent_app.ainvoke(inputs)
        
        # Extract the final response
        final_message = result["messages"][-1]
        response_content = final_message.content
        
        # Build OpenAI-compatible response
        completion_id = f"chatcmpl-{int(time.time())}"
        response = ChatCompletionResponse(
            id=completion_id,
            created=int(time.time()),
            model=request.model,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": 0,  # Not tracked in this implementation
                "completion_tokens": 0,
                "total_tokens": 0
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api_server:api",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

def main():
    """Entry point for CLI command: lena-agent-api"""
    uvicorn.run(
        "api_server:api",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

