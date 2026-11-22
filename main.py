Python

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("segunda-feira")

app = FastAPI(title="Segunda-Feira", version="3.0.0")

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
client = genai.Client(api_key=API_KEY) if API_KEY else None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)


@app.get("/")
async def home():
    if not INDEX_FILE.is_file():
        raise HTTPException(
            status_code=500,
            detail="index.html não encontrado no servidor."
        )
    return FileResponse(INDEX_FILE)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/status")
async def api_status():
    return {
        "app": "Segunda-Feira",
        "status": "online",
        "ia_configurada": client is not None,
        "modelo": MODEL_NAME,
        "interface_encontrada": INDEX_FILE.is_file(),
    }


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="A chave GEMINI_API_KEY não está configurada no Render."
        )

    contents = []

    for item in payload.history[-20:]:
        contents.append({
            "role": "model" if item.role == "assistant" else "user",
            "parts": [{"text": item.content}],
        })

    contents.append({
        "role": "user",
        "parts": [{"text": payload.message}],
    })

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config={
                "system_instruction": (
                    "Você é Segunda-Feira, uma assistente virtual "
                    "em português do Brasil. Seja clara, prática, "
                    "cordial e honesta. Ajude com organização, ideias, "
                    "produtos, clientes, vendas e finanças. Não afirme "
                    "que realizou compras, pagamentos, transferências "
                    "ou publicações. Peça autorização explícita antes "
                    "de qualquer ação externa."
                )
            },
        )

        answer = (response.text or "").strip()

        if not answer:
            raise RuntimeError("O Gemini retornou uma resposta vazia.")

        return {"reply": answer, "model": MODEL_NAME}

    except Exception as exc:
        logger.exception("Erro ao consultar Gemini")
        raise HTTPException(
            status_code=502,
            detail=(
                "Não consegui obter resposta do Gemini agora. "
                "Verifique a chave e os logs do Render."
            ),
        ) from exc
