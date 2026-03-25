"""Servidor FastAPI com streaming SSE para o agente."""
import json
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage

load_dotenv()


@tool
def consultar_clima(cidade: str) -> str:
    """Consulta a previsão do tempo para uma cidade."""
    previsoes = {
        "são paulo": "25°C, parcialmente nublado",
        "rio de janeiro": "32°C, ensolarado",
        "curitiba": "15°C, chuva leve",
    }
    return previsoes.get(cidade.lower(), f"Previsão não disponível para {cidade}.")


agente = create_agent(
    model="gpt-4.1-nano",
    tools=[consultar_clima],
    system_prompt="Você é um assistente meteorológico. Responda em português.",
)

app = FastAPI()


class Pergunta(BaseModel):
    mensagem: str


async def gerar_stream(mensagem: str):
    async for chunk in agente.astream(
        {"messages": [HumanMessage(content=mensagem)]},
        stream_mode="messages",
    ):
        msg, metadata = chunk
        if msg.content and metadata.get("langgraph_node") == "model":
            yield f"data: {json.dumps({'token': msg.content})}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/chat")
async def chat(pergunta: Pergunta):
    return StreamingResponse(
        gerar_stream(pergunta.mensagem),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
