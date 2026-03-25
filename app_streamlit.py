"""App Streamlit com streaming do agente."""
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


@st.cache_resource
def criar_agente():
    return create_agent(
        model="gpt-4.1-nano",
        tools=[consultar_clima],
        system_prompt="Você é um assistente meteorológico. Responda em português.",
        checkpointer=InMemorySaver(),
    )


agente = criar_agente()

st.title("Assistente Meteorológico")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Pergunte sobre o clima..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        config = {"configurable": {"thread_id": "streamlit-session"}}

        def gerar_tokens():
            for chunk in agente.stream(
                {"messages": [HumanMessage(content=prompt)]},
                stream_mode="messages",
                config=config,
            ):
                msg, metadata = chunk
                if msg.content and metadata.get("langgraph_node") == "model":
                    yield msg.content

        resposta = st.write_stream(gerar_tokens())

    st.session_state.messages.append({"role": "assistant", "content": resposta})
