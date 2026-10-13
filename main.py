import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI

app = FastAPI(title="AI Chat API")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def health():
    return {"status": "ok", "service": "AI Chat API"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="AI API key is not configured"
        )

    # Validate incoming roles before forwarding messages.
    if any(m.role not in ("user", "assistant")
           for m in request.messages):
        raise HTTPException(
            status_code=400,
            detail="Invalid message role"
        )

    try:
        response = client.responses.create(
            model=os.environ.get(
                "OPENAI_MODEL", "gpt-4.1-mini"
            ),
            input=[
                {
                    "role": m.role,
                    "content": m.content
                }
                for m in request.messages
            ]
        )

        return ChatResponse(reply=response.output_text)

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI provider request failed"
        )
