import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("segunda-feira")

API_KEY = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
MODEL_NAME = (os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite").strip()

client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_INSTRUCTION = (
    "Você é Segunda-Feira, uma assistente virtual "
    "em português do Brasil. Seja clara, prática, "
    "cordial e honesta. Ajude com organização, ideias, "
    "produtos, clientes, vendas e finanças. Não afirme "
    "que realizou compras, pagamentos, transferências "
    "ou publicações. Peça autorização explícita antes "
    "de qualquer ação externa."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if client is not None:
        await client.aio.aclose()


app = FastAPI(title="Segunda-Feira", version="3.0.0", lifespan=lifespan)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)

    @field_validator("content")
    @classmethod
    def not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("A mensagem não pode estar vazia.")
        return cleaned


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("A mensagem não pode estar vazia.")
        return cleaned


@app.get("/")
async def home():
    if not INDEX_FILE.is_file():
        raise HTTPException(
            status_code=500,
            detail="index.html não encontrado no servidor.",
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
            detail="A chave GEMINI_API_KEY não está configurada no Render.",
        )

    history = payload.history[-20:]
    # Garante que o histórico não comece com fala do modelo após o slice
    while history and history[0].role == "assistant":
        history = history[1:]

    contents = [
        types.Content(
            role="model" if item.role == "assistant" else "user",
            parts=[types.Part.from_text(text=item.content)],
        )
        for item in history
    ]
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=payload.message)],
        )
    )

    try:
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            ),
        )

        answer = (response.text or "").strip()
        if not answer:
            raise RuntimeError("O Gemini retornou uma resposta vazia.")

        return {"reply": answer, "model": MODEL_NAME}

    except errors.APIError as exc:
        logger.exception("Erro da API do Gemini (status %s)", exc.code)
        if exc.code == 429:
            raise HTTPException(
                status_code=429,
                detail="Limite de requisições do Gemini atingido. Tente novamente em instantes.",
            ) from exc
        raise HTTPException(
            status_code=502,
            detail="Erro ao consultar o Gemini. Verifique a chave, o modelo e os logs do Render.",
        ) from exc

    except Exception as exc:
        logger.exception("Erro inesperado ao consultar Gemini")
        raise HTTPException(
            status_code=502,
            detail="Não consegui obter resposta do Gemini agora. Verifique os logs do Render.",
        ) from exc
