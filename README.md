# Chatbot Payroll

Um chatbot em Python para responder perguntas sobre folha de pagamento com suporte a consultas em linguagem natural, utilizando:

- FastAPI no backend
- Streamlit no frontend
- LangChain + Gemini API para entendimento de linguagem natural
- SQLite (gerado do CSV) para consultas estruturadas
- Pytest para testes automatizados

---

## 🛠 Tecnologias usadas

- Python 3.13
- Streamlit
- FastAPI + Uvicorn
- LangChain (com `langchain-google-genai`)
- Pandas (manipulação de dados)
- python-dotenv (variáveis de ambiente)
- Pytest (testes)

---

## 🚀 Funcionalidades

- Chat básico com LLM (Gemini).

- Consultas à folha de pagamento via RAG/SQL:

-- Líquido recebido em determinado mês.

-- Totais por período (ex.: trimestre).

-- Bônus, descontos (INSS, IRRF) e data de pagamento.

- Respostas formatadas em BRL (R$ 1.234,56) e datas no formato dd/mm/aaaa.

- Evidências claras (sempre cita employee_id e competency).

- Testes de integração garantindo respostas consistentes.

---

## 📂 Estrutura do projeto

```
chatbot-payroll/
├── app/
│   ├── __init__.py
│   ├── chatbot.py       # Core do chatbot (LLM, SQL, RAG)
│   ├── data_to_db.py    # Converte CSV → SQLite
│   ├── main.py          # API FastAPI
│   └── utils.py         # Funções utilitárias
├── data/
│   └── payroll.csv      # Dataset oficial
├── frontend/
│   └── app.py           # Interface em Streamlit
├── tests/
│   ├── test_chatbot.py  # Testes automatizados (Pytest)
│   └── test_utils.py    # Testes unitários
├── .env.example         # Exemplo de configuração
├── pyproject.toml       # Dependências (Poetry)
└── README.md
```

---

## ⚙️ Setup

1. **Instalar Poetry** (se ainda não tiver):

```
pip install poetry
```

2. **Clonar repositório e entrar na pasta:**

```
git clone https://github.com/seuuser/chatbot-payroll.git
cd chatbot-payroll
```

3. **Instalar dependências:**

```
poetry install
```

4. **Configurar variáveis de ambiente:**

```
GEMINI_API_KEY=coloque_sua_chave_aqui
```

5. **Prepare o banco de dados:**

### O banco SQLite será gerado automaticamente a partir do payroll.csv na primeira execução.

---

## 🚀 Execução

Rodar API (FastAPI):

```
poetry run python app/main.py
```

A API sobe em http://localhost:8000.

## Rodar frontend (Streamlit):

```
poetry run streamlit run frontend/app.py
```

- Digite sua pergunta na interface e o chatbot irá responder.
- Para consultas sobre folha de pagamento, ele também retorna evidência em JSON.

---

## 🧪 Rodar testes

```
poetry run pytest -v
```

Os testes cobrem:

1. Consulta simples (líquido por mês)

"Quanto recebi (líquido) em maio/2025? (Ana Souza)"

Esperado: R$ 8.418,75. Fonte: E001, 2025-05.

2. Consulta agregada (trimestre)

"Qual o total líquido de Ana Souza no 1º trimestre de 2025?"

Esperado: R$ 23.221,25 (jan+fev+mar). Fontes: E001, 2025-01..03.

3. Consulta com BRL e datas

"Quando foi pago o salário de abril/2025 do Bruno e qual o líquido?"

Esperado: 28/04/2025 e R$ 5.756,25. Fonte: E002, 2025-04.

---

## 📝 Decisões técnicas

- Poetry: gerenciamento de dependências e ambientes isolados.
- LangChain: usado para parsing de linguagem natural e integração com Gemini.
- SQLite: banco leve e embutido, populado a partir do CSV.
- Fallback heurístico: caso o LLM falhe na extração de parâmetros, regex simples cobre os principais casos.
- Decimal: usado para cálculos financeiros (evita erros de arredondamento com float).

---

## ⚠️ Limitações

- Dependência da API Gemini (mesmo com fallback, consultas mais complexas podem exigir tokens).
- O parsing via LLM ainda pode falhar em perguntas muito ambíguas.
- Dataset sintético e fixo (payroll.csv).
- Algumas respostas dependem de heurísticas simplificadas (ex.: trimestres fixos).

---

## 🚀 Próximos passos (melhorias)

- Adicionar memória de conversa para manter contexto entre perguntas.
- Expandir fallback heurístico para cobrir mais variações de linguagem.
- Implementar testes de carga e robustez.
- Melhorar UX no Streamlit com botões de exportar evidências.
- Adicionar suporte opcional a busca na web com fontes externas.
