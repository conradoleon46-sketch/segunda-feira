# Segunda-Feira 3.0

Projeto inicial do agente pessoal Segunda-Feira 3.0. Esta versão fornece uma API simples para conversar com o agente e está preparada para implantação no Render.

## O que esta versão já oferece

- API web com rota inicial (`/`) e verificação de saúde (`/health`).
- Rota de conversa (`POST /chat`) usando a API da OpenAI.
- Orientações de segurança: nenhuma compra, pagamento, transferência ou publicação é feita automaticamente.
- Arquivo `render.yaml` para facilitar a configuração no Render.

## Importante

Esta é uma **versão inicial funcional da estrutura**, não um sistema comercial completo. Pesquisa automática de fornecedores/clientes, gestão persistente de vendas, integrações e automações ainda precisam ser desenvolvidas e testadas. Para ativar as respostas de IA, é necessária uma chave da API da OpenAI configurada como variável de ambiente `OPENAI_API_KEY` no Render. Não coloque essa chave no GitHub nem a envie no chat.

## Publicar no GitHub pelo celular

1. Baixe e extraia o ZIP.
2. Abra o repositório `segunda-feira` no GitHub.
3. Toque em **Add file** e depois **Upload files**.
4. Envie os arquivos e pastas que estão dentro da pasta `segunda-feira-3.0` (não envie o ZIP fechado).
5. Toque em **Commit changes** para salvar.

## Publicar no Render

1. No Render, crie um **New Web Service** e conecte sua conta do GitHub.
2. Escolha o repositório `segunda-feira`.
3. O Render pode detectar as configurações de `render.yaml`. Se pedir manualmente: Build Command `pip install -r requirements.txt`; Start Command `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Em **Environment**, adicione `OPENAI_API_KEY` com sua chave da API. Mantenha-a privada.
5. Faça o deploy. A rota `/health` deve responder `{"status":"ok"}`.

## Teste local (opcional)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

A documentação interativa fica em `/docs`.
