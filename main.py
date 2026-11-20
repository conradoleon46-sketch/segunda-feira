import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Segunda-Feira 3.0", version="0.1.0")

SYSTEM_PROMPT = """Você é o Segunda-Feira 3.0, um assistente em português do Brasil focado em ajudar o usuário a pesquisar oportunidades comerciais, organizar ideias, planejar anúncios, acompanhar vendas, despesas e lucros. Seja claro, prático e honesto. Nunca invente preços, fornecedores, clientes ou resultados. Não faça pagamentos, compras, transferências, publicação de anúncios ou contato com terceiros sem autorização explícita do usuário. Peça confirmação antes de qualquer ação externa ou financeira. Não solicite senhas, códigos de autenticação ou chaves secretas no chat."""

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def home():
    return {"app": "Segunda-Feira 3.0", "status": "online", "version": "0.1.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Configure OPENAI_API_KEY nas variáveis de ambiente do Render para ativar o chat.")
    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=SYSTEM_PROMPT,
            input=payload.message,
        )
        return ChatResponse(reply=response.output_text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao consultar o serviço de IA: {type(exc).__name__}")
