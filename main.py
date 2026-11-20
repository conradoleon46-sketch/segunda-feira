
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Segunda-Feira 3.0")


class ChatMessage(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Segunda-Feira 3.0</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #101522;
    color: white;
}
header {
    background: #192338;
    padding: 22px;
    text-align: center;
    border-bottom: 1px solid #34415b;
}
header h1 { margin: 0; font-size: 24px; }
header p { color: #9eacc5; margin-bottom: 0; }
main {
    max-width: 700px;
    margin: auto;
    padding: 18px;
}
.status {
    color: #65e6a3;
    text-align: center;
    margin: 12px;
}
#chat {
    height: 55vh;
    min-height: 300px;
    overflow-y: auto;
    background: #192338;
    border-radius: 14px;
    padding: 15px;
}
.message {
    padding: 12px 14px;
    margin: 10px 0;
    border-radius: 12px;
    line-height: 1.5;
    max-width: 90%;
    white-space: pre-wrap;
}
.bot { background: #293751; }
.user {
    background: #245cba;
    margin-left: auto;
}
.controls {
    display: flex;
    gap: 8px;
    margin-top: 14px;
}
input {
    flex: 1;
    min-width: 0;
    padding: 15px;
    border: 0;
    border-radius: 10px;
    font-size: 16px;
}
button {
    border: 0;
    border-radius: 10px;
    padding: 12px 18px;
    background: #3979e8;
    color: white;
    font-size: 16px;
    font-weight: bold;
}
button:disabled { opacity: .5; }
footer {
    color: #8998b2;
    text-align: center;
    font-size: 12px;
    padding: 20px;
}
</style>
</head>
<body>
<header>
    <h1>Segunda-Feira 3.0</h1>
    <p>Seu assistente pessoal</p>
</header>
<main>
    <div class="status">● Sistema online</div>
    <div id="chat">
        <div class="message bot">
            Olá! Eu sou o Segunda-Feira 3.0.
            Esta é minha nova interface.
            Pode escrever uma mensagem abaixo!
        </div>
    </div>
    <div class="controls">
        <input id="message" placeholder="Digite sua mensagem..."
               autocomplete="off">
        <button id="send" onclick="sendMessage()">Enviar</button>
    </div>
</main>
<footer>Segunda-Feira 3.0 · Assistente pessoal</footer>
<script>
const input = document.getElementById("message");
const chat = document.getElementById("chat");
const send = document.getElementById("send");

function addMessage(text, type) {
    const item = document.createElement("div");
    item.className = "message " + type;
    item.textContent = text;
    chat.appendChild(item);
    chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
    const message = input.value.trim();
    if (!message || send.disabled) return;

    addMessage(message, "user");
    input.value = "";
    send.disabled = true;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message})
        });

        if (!response.ok) throw new Error("Erro no servidor");

        const data = await response.json();
        addMessage(data.reply, "bot");
    } catch (error) {
        addMessage("Não consegui enviar agora. Tente novamente.", "bot");
    }

    send.disabled = false;
    input.focus();
}

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") sendMessage();
});
</script>
</body>
</html>
"""


@app.post("/api/chat")
def chat(message: ChatMessage):
    return {
        "reply": (
            "Recebi sua mensagem: "
            + message.message
            + ". Minha interface está funcionando! "
            "A conexão com a inteligência do agente ainda será configurada."
        )
    }
