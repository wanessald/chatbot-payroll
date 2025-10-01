import pytest
from app.chatbot import PayrollChatbot


@pytest.fixture(scope="module")
def bot():
    # Instancia o chatbot sem depender do LLM (não chama o .chat)
    return PayrollChatbot()


def test_liquido_por_mes(bot):
    params = {
        "intent": "payroll_query",
        "name": "Ana Souza",
        "competency": "2025-05",
        "data_type": "net_pay",
    }
    resposta = bot._handle_payroll_query(params)
    assert "R$ 8.418,75" in resposta
    assert "E001, 2025-05" in resposta


def test_total_trimestre(bot):
    params = {
        "intent": "payroll_query",
        "name": "Ana Souza",
        "period_start": "2025-01",
        "period_end": "2025-03",
        "data_type": "net_pay",
    }
    resposta = bot._handle_payroll_query(params)
    assert "R$ 23.221,25" in resposta
    assert "E001, 2025-01" in resposta
    assert "E001, 2025-03" in resposta


def test_data_pagamento_com_liquido(bot):
    params = {
        "intent": "payroll_query",
        "name": "Bruno Lima",
        "competency": "2025-04",
        "data_type": "payment_date",
    }
    resposta = bot._handle_payroll_query(params)
    assert "28/04/2025" in resposta
    assert "R$ 5.756,25" in resposta
    assert "E002, 2025-04" in resposta
