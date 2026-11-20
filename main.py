
import os
import asyncio
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

app = FastAPI(title="Segunda-Feira 3.0")

MODEL = "gemini-3.8-flash"

SYSTEM_PROMPT = """
Você é o Segunda-Feira 3.0, um assistente pessoal inteligente,
prestativo, organizado e direto.

Seu objetivo é ajudar o usuário a:
- Encontrar oportunidades de renda e negócios.
- Pesquisar produtos, fornecedores e clientes.
- Criar anúncios e ofertas comerciais.
- Organizar vendas, despesas e lucros.
- Planejar tarefas e automatizações.

Converse sempre em português brasileiro.
Explique assuntos técnicos de maneira simples.
Nunca afirme que realizou uma compra, pagamento ou
movimentação financeira sem autorização explícita.
Não invente informações nem diga que executou ações
que não foram realmente realizadas.
"""

HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#101827">
<title>Segunda-Feira 3.0</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background: #0b1120;
    color: #edf2f7;
    font-family: Arial, sans-serif;
}

.app {
    width: 100%;
    max-width: 950px;
    min-height: 100vh;
    margin: auto;
    display: flex;
    flex-direction: column;
    background: #111a2b;
}

header {
    padding: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    background: #17243a;
    border-bottom: 1px solid #293750;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo {
    width: 46px;
    height: 46px;
    display: grid;
    place-items: center;
    border-radius: 14px;
    background: linear-gradient(135deg, #20c997, #087f8c);
    color: #061923;
    font-size: 24px;
    font-weight: bold;
}

h1 {
    font-size: 19px;
    margin: 0 0 5px;
}

.status {
    color: #7ce7bd;
    font-size: 12px;
}

.clear {
    border: 1px solid #41516a;
    background: transparent;
    color: #cbd5e1;
    padding: 10px 12px;
    border-radius: 9px;
    cursor: pointer;
}

.welcome {
    padding: 28px 20px 12px;
}

.welcome h2 {
    margin: 0 0 8px;
    font-size: 23px;
}

.welcome p {
    color: #9eacc1;
    line-height: 1.5;
    margin: 0;
}

.suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    padding: 15px 20px;
}

.suggestion {
    background: #1b2a40;
    border: 1px solid #344761;
    color: #d6e6f5;
    border-radius: 20px;
    padding: 9px 13px;
    cursor: pointer;
}

.suggestion:hover {
    background: #263c56;
}

#chat {
    flex: 1;
    min-height: 300px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.message {
    max-width: 85%;
    padding: 13px 16px;
    border-radius: 16px;
    line-height: 1.55;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.bot {
    align-self: flex-start;
    background: #1e2c42;
    border: 1px solid #30445f;
    border-bottom-left-radius: 4px;
}

.user {
    align-self: flex-end;
    background: #087f70;
    color: white;
    border-bottom-right-radius: 4px;
}

.message-label {
    display: block;
    font-size: 11px;
    opacity: .7;
    margin-bottom: 5px;
}

.typing {
    color: #7ce7bd;
    font-size: 13px;
    padding: 0 20px 12px;
}

.composer {
    position: sticky;
    bottom: 0;
    background: #17243a;
    border-top: 1px solid #293750;
    padding: 15px;
}

.input-area {
    display: flex;
    gap: 10px;
}

input {
    min-width: 0;
    flex: 1;
    padding: 15px;
    background: #0d1728;
    border: 1px solid #3b506d;
    border-radius: 12px;
    color: white;
    font-size: 16px;
    outline: none;
}

input:focus {
    border-color: #20c997;
}

.send {
    border: 0;
    border-radius: 12px;
    padding: 0 20px;
    background: #20c997;
    color: #06251e;
    font-weight: bold;
    cursor: pointer;
}

.send:disabled {
    opacity: .5;
    cursor: wait;
}

.footer {
    text-align: center;
    color: #8191a8;
    font-size: 11px;
    padding-top: 12px;
}

@media (max-width: 500px) {
    header { padding: 14px; }
    .welcome { padding-top: 22px; }
    #chat { padding: 15px; }
    .message { max-width: 92%; }
    .clear { font-size: 11px; }
}
</style>
</head>

<body>
<div class="app">

<header>
    <div class="brand">
        <div class="logo">S</div>
        <div>
            <h1>Segunda-Feira 3.0</h1>
            <div class="status">● Assistente conectado à interface</div>
        </div>
    </div>
    <button class="clear" onclick="clearChat()">
        Limpar conversa
    </button>
</header>

<section class="welcome">
    <h2>Olá! Como posso ajudar?</h2>
    <p>
        Estou aqui para ajudar você a organizar ideias,
        encontrar oportunidades e desenvolver seus projetos.
    </p>
</section>

<div class="suggestions">
    <button class="suggestion"
        onclick="useSuggestion('Quero encontrar oportunidades para ganhar dinheiro.')">
        💰 Ideias de renda
    </button>
    <button class="suggestion"
        onclick="useSuggestion('Me ajude a organizar minhas finanças.')">
        📊 Finanças
    </button>
    <button class="suggestion"
        onclick="useSuggestion('Quero pesquisar produtos para vender.')">
        🛒 Produtos
    </button>
</div>

<main id="chat" aria-live="polite">
    <div class="message bot">
        <span class="message-label">SEGUNDA-FEIRA</span>
        Olá! Sou o Segunda-Feira 3.0. Pode conversar comigo!
    </div>
</main>

<div id="typing" class="typing" hidden>
    Segunda-Feira está pensando...
</div>

<section class="composer">
    <div class="input-area">
        <input
            id="message"
            type="text"
            maxlength="4000"
            placeholder="Escreva sua mensagem..."
            autocomplete="off"
        >
        <button id="send" class="send" onclick="sendMessage()">
            Enviar
        </button>
    </div>
    <div class="footer">
        Segunda-Feira 3.0 • Seu assistente pessoal
    </div>
</section>

</div>

<script>
const chat = document.getElementById("chat");
const input = document.getElementById("message");
const sendButton = document.getElementById("send");
const typing = document.getElementById("typing");

let history = [];

function addMessage(text, role) {
    const bubble = document.createElement("div");
    bubble.className = "message " + role;

    const label = document.createElement("span");
    label.className = "message-label";
    label.textContent = role === "user" ? "VOCÊ" : "SEGUNDA-FEIRA";

    const content = document.createElement("div");
    content.textContent = text;

    bubble.appendChild(label);
    bubble.appendChild(content);
    chat.appendChild(bubble);

    chat.scrollTop = chat.scrollHeight;
    return bubble;
}

function useSuggestion(text) {
    input.value = text;
    sendMessage();
}

function clearChat() {
    if (!confirm("Deseja limpar esta conversa?")) return;

    history = [];
    chat.innerHTML = "";

    addMessage(
        "Conversa limpa! Como posso ajudar agora?",
        "bot"
    );
}

async function sendMessage() {
    const message = input.value.trim();

    if (!message || sendButton.disabled) return;

    addMessage(message, "user");

    const previousHistory = [...history];

    history.push({
        role: "user",
        content: message
    });

    input.value = "";
    sendButton.disabled = true;
    typing.hidden = false;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                history: previousHistory
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Erro ao conversar.");
        }

        addMessage(data.response, "bot");

        history.push({
            role: "model",
            content: data.response
        });

    } catch (error) {
        addMessage(
            "Não consegui obter uma resposta. " +
            error.message,
            "bot"
        );

        history.pop();
    } finally {
        typing.hidden = true;
        sendButton.disabled = false;
        input.focus();
    }
}

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
</script>

</body>
</html>
"""

class HistoryMessage(BaseModel):
    role: Literal["user", "model"]
    content: str = Field(min_length=1, max_length=4000)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=20)

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

def ask_gemini(message, history):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("A chave do Gemini não está configurada.")

    client = genai.Client(api_key=api_key)

    contents = []

    for item in history:
        contents.append(
            types.Content(
                role=item.role,
                parts=[types.Part.from_text(text=item.content)]
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        )
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=1500
        )
    )

    if not response.text:
        raise RuntimeError("O Gemini não retornou texto.")

    return response.text

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        answer = await asyncio.to_thread(
            ask_gemini,
            request.message,
            request.history
        )

        return {"response": answer}

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Não consegui conversar com o Gemini. Tente novamente."
        )
