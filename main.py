import asyncio
import logging
import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from google import genai

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("segunda-feira")

APP_NAME = "Segunda-Feira 3.0"
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

app = FastAPI(title=APP_NAME, version="3.0.0")

SYSTEM_INSTRUCTION = """Você é Segunda-Feira, um agente pessoal inteligente, estrategista e assistente de negócios.
Sua missão é ajudar o usuário a encontrar oportunidades para ganhar dinheiro e desenvolver fontes de renda.
Ajude a planejar pequenos negócios, avaliar ideias, pesquisar produtos e fornecedores quando houver ferramentas de pesquisa realmente disponíveis, organizar clientes e vendas, controlar receitas, despesas, custos e lucros, criar anúncios, organizar tarefas, metas e missões e avaliar resultados.
Fale sempre em português brasileiro. Seja claro, prático, organizado, criativo e objetivo.
Nunca invente pesquisas, preços, fornecedores, clientes, vendas ou ações realizadas. Se não tiver acesso a uma ferramenta ou dado, explique isso claramente e ajude com um plano alternativo.
Não diga que salvou dados no servidor: os registros do painel ficam armazenados localmente no navegador deste dispositivo.
Nunca realize pagamentos, compras, transferências, publicações ou qualquer ação externa sem autorização expressa do usuário.
Transforme ideias em planos práticos e executáveis. Quando possível, apresente passos, custos estimados identificados como estimativas e riscos."""


class HistoryMessage(BaseModel):
    role: Literal["user", "model", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=30)


@app.get("/", include_in_schema=False)
async def home():
    if not INDEX_FILE.is_file():
        logger.error("index.html ausente em %s", INDEX_FILE)
        raise HTTPException(status_code=500, detail="A interface index.html não foi publicada junto com main.py.")
    return FileResponse(INDEX_FILE, media_type="text/html; charset=utf-8")


@app.get("/api/status")
async def status():
    return {
        "app": APP_NAME,
        "status": "online",
        "ia_configurada": client is not None,
        "modelo": MODEL,
        "interface_encontrada": INDEX_FILE.is_file(),
    }


def ask_gemini(message: str, history: list[HistoryMessage]) -> str:
    if client is None:
        raise RuntimeError("A chave GEMINI_API_KEY não está configurada no Render.")

    contents = []
    for item in history[-20:]:
        role = "model" if item.role in ("model", "assistant") else "user"
        contents.append({"role": role, "parts": [{"text": item.content}]})
    contents.append({"role": "user", "parts": [{"text": message}]})

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config={"system_instruction": SYSTEM_INSTRUCTION, "temperature": 0.7},
    )
    answer = getattr(response, "text", None)
    return answer.strip() if answer and answer.strip() else "Não consegui formular uma resposta. Tente novamente."


@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Digite uma mensagem antes de enviar.")
    try:
        answer = await asyncio.to_thread(ask_gemini, message, request.history)
        return {"response": answer}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Falha ao conversar com Gemini")
        raise HTTPException(status_code=502, detail="Falha ao acessar o Gemini. Confira a chave e os logs do Render.") from exc


@app.get("/health")
async def health():
    return {"status": "ok", "app": APP_NAME}
