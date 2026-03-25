"""App Streamlit com visibilidade de tool calls."""
import streamlit as st
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

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


@tool
def buscar_restaurantes(cidade: str, tipo: str) -> str:
    """Busca restaurantes em uma cidade por tipo de culinária."""
    return f"3 restaurantes de {tipo} em {cidade}: A, B, C."


@st.cache_resource
def criar_agente():
    return create_agent(
        model="gpt-4.1-nano",
        tools=[consultar_clima, buscar_restaurantes],
        system_prompt="Você é um assistente de viagem.",
        checkpointer=InMemorySaver(),
    )


agente = criar_agente()

st.title("Assistente de Viagem")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Pergunte sobre viagem..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        config = {"configurable": {"thread_id": "streamlit-tools"}}
        status_container = st.empty()

        tool_calls_seen = []

        def gerar_tokens():
            for chunk in agente.stream(
                {"messages": [HumanMessage(content=prompt)]},
                stream_mode=["messages", "updates"],
                config=config,
            ):
                mode, data = chunk
                if mode == "updates":
                    for node_name, update in data.items():
                        if node_name == "tools":
                            for msg in update.get("messages", []):
                                tool_calls_seen.append(msg.name)
                                status_container.info(f"Ferramenta: {msg.name}")
                elif mode == "messages":
                    msg, metadata = data
                    if msg.content and metadata.get("langgraph_node") == "model":
                        yield msg.content

        resposta = st.write_stream(gerar_tokens())
        status_container.empty()

    st.session_state.messages.append({"role": "assistant", "content": resposta})
