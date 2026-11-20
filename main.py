import os
import logging
import asyncio
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from google import genai

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("segunda-feira")

app = FastAPI(title="Segunda-Feira")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=API_KEY) if API_KEY else None


# Estrutura das mensagens
class HistoryMessage(BaseModel):
    role: Literal["user", "model", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[HistoryMessage] = Field(default_factory=list)


# Página principal
@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return HTMLResponse(
            "<h1>Segunda-Feira</h1>"
            "<p>Arquivo index.html não encontrado.</p>",
            status_code=404
        )


# Estado do aplicativo
@app.get("/api/status")
async def status():
    return {
        "app": "Segunda-Feira",
        "status": "online",
        "ia_configurada": client is not None,
        "modelo": MODEL
    }


# Inteligência artificial
def ask_gemini(message, history):
    if client is None:
        raise RuntimeError(
            "Configure GEMINI_API_KEY nas variáveis do Render."
        )

    contents = []

    for item in history[-20:]:
        role = "model" if item.role == "assistant" else item.role

        contents.append({
            "role": role,
            "parts": [{"text": item.content}]
        })

    contents.append({
        "role": "user",
        "parts": [{"text": message}]
    })

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config={
            "system_instruction": """
Você é Segunda-Feira, um agente pessoal inteligente,
estrategista e assistente de negócios.

Sua missão é ajudar o usuário a encontrar oportunidades
para ganhar dinheiro e desenvolver novas fontes de renda.

Ajude a:
- Encontrar oportunidades de negócios.
- Pesquisar produtos e fornecedores quando houver
  ferramentas de pesquisa disponíveis.
- Planejar pequenos negócios.
- Organizar clientes e vendas.
- Controlar receitas, despesas, custos e lucros.
- Criar anúncios e estratégias comerciais.
- Organizar tarefas, metas e missões.
- Avaliar resultados e sugerir melhorias.

Fale sempre em português brasileiro.
Seja organizado, criativo, inteligente e objetivo.

Não invente pesquisas, preços, fornecedores ou ações.
Se não tiver acesso a uma ferramenta, explique isso.

Nunca realize pagamentos, compras, transferências
ou publicações sem autorização expressa do usuário.

Transforme ideias em planos práticos e executáveis.
"""
        }
    )

    return response.text or "Não consegui gerar uma resposta."


# Chat do agente
@app.post("/api/chat")
async def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Digite uma mensagem."
        )

    try:
        answer = await asyncio.to_thread(
            ask_gemini,
            request.message,
            request.history
        )

        return {"response": answer}

    except Exception:
        logger.exception("Erro ao conversar com Gemini")

        raise HTTPException(
            status_code=502,
            detail=(
                "Não consegui acessar a inteligência artificial. "
                "Confira a chave Gemini e os logs do Render."
            )
        )


# Verificação do servidor
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "Segunda-Feira"
    }
