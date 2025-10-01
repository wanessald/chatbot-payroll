import streamlit as st
import requests
import json
import os

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

st.set_page_config(page_title="Chatbot de Folha de Pagamento")

st.title("💰 Chatbot de Folha de Pagamento")
st.write("Pergunte sobre sua folha de pagamento ou converse sobre outros assuntos!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("evidence"):
            st.json(message["evidence"])

if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = requests.post(
            f"{FASTAPI_URL}/chat",
            json={"message": prompt},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "Nenhuma resposta gerada.")
            evidence = data.get("evidence")
            st.session_state.messages.append({"role": "assistant", "content": answer, "evidence": evidence})
            with st.chat_message("assistant"):
                st.markdown(answer)
                if evidence:
                    st.json(evidence)
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Erro ao consultar backend: {response.status_code}"})
            with st.chat_message("assistant"):
                st.markdown(f"Erro ao consultar backend: {response.status_code}")
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Erro: {str(e)}"})
        with st.chat_message("assistant"):
            st.markdown(f"Erro: {str(e)}")

    