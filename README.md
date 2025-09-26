# Chatbot Payroll

Este projeto é um chatbot inteligente para responder dúvidas sobre folha de pagamento, utilizando LLM local e RAG para consultas precisas em dados reais.

---

## 🛠 Tecnologias usadas

- Python 3.13
- Streamlit
- Ollama (LLM local)
- Pandas (manipulação de dados)
- python-dotenv (variáveis de ambiente)
- Pytest (testes)

---

## 📂 Estrutura do projeto

chatbot-payroll/
```
├── data/
├── src/
│ ├── main.py
│ ├── llm.py
│ ├── rag.py
│ ├── utils.py
│ └── config.py
├── tests/
├── pyproject.toml
├── poetry.lock
├── .env.example
└── README.md
```
---

## ⚡ Setup inicial

1. **Instalar Poetry** (se ainda não tiver):

```
pip install poetry
```

2. **Clonar repositório e entrar na pasta:**

```
git clone https://github.com/seuuser/chatbot-payroll.git
cd chatbot-payroll
```

3. **Instalar dependências e criar virtualenv:**

```
poetry install
```

4. **Configurar variáveis de ambiente:**

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`. Nele, você pode definir variáveis como o modelo do Ollama, chaves de API e URLs de serviços externos, por exemplo:

```
OLLAMA_MODEL=llama3
API_KEY=sua-chave-aqui
SERVICE_URL=https://api.exemplo.com
```

---

## 🚀 Como rodar

```
poetry run streamlit run src/main.py
```

- Digite sua pergunta na interface e o chatbot irá responder.
- Para consultas sobre folha de pagamento, ele também retorna evidência em JSON.

---

## 🧪 Rodar testes

```
poetry run pytest -v
```

---

## 📝 Decisões técnicas

- src/: separação do código fonte do projeto, evitando problemas de importação e melhor organização.
- RAG simples com Pandas: consulta direta no CSV com filtros e retorna evidências.
- LLM Ollama local: permite respostas gerais e contexto da folha.
- Poetry: gerenciamento moderno de dependências, ambiente virtual isolado e lockfile para reprodutibilidade.
