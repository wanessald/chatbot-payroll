import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from decimal import Decimal
from app.utils import format_date_br
from app.data_to_db import query_payroll_data, csv_to_sqlite
from app.utils import format_currency, parse_date_input

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class PayrollChatbot:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não configurada. Verifique seu arquivo .env.")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY)
        self.history = [] 
        csv_to_sqlite("data/payroll.csv", "data/payroll.db")
        self.system_prompt = (
            "Você é um chatbot especializado em folha de pagamento, mas também capaz de conversar sobre assuntos gerais. "
            "Para perguntas sobre folha de pagamento, consulte os dados disponíveis. "
            "Sempre que responder a uma pergunta sobre folha de pagamento, cite a fonte usando 'employee_id' e 'competency'. "
            "Formate valores monetários em BRL (Ex: R$ 1.234,56) e datas em dd/mm/aaaa. "
            "Se não encontrar informações específicas sobre folha de pagamento, informe ao usuário. "
        )

    def _extract_payroll_intent_and_params(self, user_query: str):
        """
        Usa o LLM para extrair intenção (payroll_query, general_chat) e parâmetros (nome, mes_ano, tipo_dado).
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                "Analise a seguinte pergunta do usuário e extraia o máximo de informações possível "
                "relacionadas à folha de pagamento, como nome do funcionário, mês/ano (competência), "
                "e o tipo de dado solicitado (líquido, bônus, INSS, IRRF, data de pagamento, etc.). "
                "Se a pergunta não for sobre folha de pagamento, indique 'general_chat'. "
                "Formato de saída esperado: JSON como {'intent': 'payroll_query'|'general_chat', 'name': '...', 'competency': 'YYYY-MM', 'data_type': '...', 'period_start': 'YYYY-MM', 'period_end': 'YYYY-MM'}"
                "Para perguntas de período, como '1º trimestre', converta para 'period_start' e 'period_end'."
            ),
            HumanMessage(content=user_query)
        ])
        try:
            extraction_chain = prompt | self.llm.bind(response_format={"type": "json_object"})
            response = extraction_chain.invoke({"user_query": user_query})
            
            parsed_response = json.loads(response.content)
            return parsed_response
        except Exception as e:
            print(f"Erro ao extrair intenção e parâmetros: {e}")
            return self._fallback_extract_params(user_query)


    def _fallback_extract_params(self, user_query: str):
        """Heurística simples para extrair parâmetros se o LLM falhar no JSON."""
        params = {"intent": "general_chat"}
        
        name_match = re.search(r"(Ana(?:\s+Souza)?|Bruno(?:\s+Lima)?)", user_query, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()
            if "ana" in name.lower():
                params["name"] = "Ana Souza"
            elif "bruno" in name.lower():
                params["name"] = "Bruno Lima"
            params["intent"] = "payroll_query"

        month_year_match = re.search(r"(janeiro|jan|fevereiro|fev|março|mar|abril|abr|maio|mai|junho|jun)\D*(\d{4})", user_query, re.IGNORECASE)
        if month_year_match:
            month_map = {"jan": "01", "fev": "02", "mar": "03", "abr": "04", "mai": "05", "jun": "06",
                         "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06"}
            month_num = month_map.get(month_year_match.group(1).lower()[:3])
            if month_num:
                params["competency"] = f"{month_year_match.group(2)}-{month_num}"
                params["intent"] = "payroll_query"
        
        if "1º trimestre" in user_query.lower():
            params["period_start"] = "2025-01"
            params["period_end"] = "2025-03"
            params["intent"] = "payroll_query"

        if "data de pagamento" in user_query.lower() or "quando foi pago" in user_query.lower():
            params["data_type"] = "payment_date"
            params["intent"] = "payroll_query"

        elif "líquido" in user_query.lower() or "recebi" in user_query.lower():
            params["data_type"] = "net_pay"
            params["intent"] = "payroll_query"
        elif "bônus" in user_query.lower():
            params["data_type"] = "bonus"
            params["intent"] = "payroll_query"
        elif "inss" in user_query.lower():
            params["data_type"] = "deductions_inss"
            params["intent"] = "payroll_query"
        elif "irrf" in user_query.lower():
            params["data_type"] = "deductions_irrf"
            params["intent"] = "payroll_query"

        return params


    def _handle_payroll_query(self, params: dict):
        """Lida com perguntas de folha de pagamento usando o banco de dados."""
        name = params.get("name")
        competency = params.get("competency")
        data_type = params.get("data_type")
        period_start = params.get("period_start")
        period_end = params.get("period_end")

        sql_where_clauses = []
        if name:
            sql_where_clauses.append(f"name = '{name}'")
        
        if competency:
            sql_where_clauses.append(f"competency = '{competency}'")
        
        if period_start and period_end:
            sql_where_clauses.append(f"competency BETWEEN '{period_start}' AND '{period_end}'")

        where_clause = " AND ".join(sql_where_clauses)
        if where_clause:
            where_clause = f" WHERE {where_clause}"

        if data_type == "net_pay" and period_start and period_end:
            sql_query = f"SELECT SUM(net_pay) as total_net_pay FROM payroll {where_clause}"
            results = query_payroll_data(sql_query)
            if results and results[0]["total_net_pay"] is not None:
                total_net_pay = Decimal(str(results[0]["total_net_pay"]))
                sources = query_payroll_data(f"SELECT employee_id, competency FROM payroll {where_clause}")
                source_str = ", ".join([f"{s['employee_id']}, {s['competency']}" for s in sources])
                return (
                    f"O total líquido de {name} de "
                    f"{parse_date_input(period_start).strftime('%b/%Y')} a {parse_date_input(period_end).strftime('%b/%Y')} foi de "
                    f"**{format_currency(total_net_pay)}**. "
                    f"Fonte: `{source_str}`."
                )
            else:
                return f"Não encontrei dados de folha de pagamento para {name} no período de {period_start} a {period_end}."

        elif data_type == "payment_date":
            sql_query = f"SELECT payment_date, net_pay, employee_id, competency FROM payroll {where_clause}"
            results = query_payroll_data(sql_query)

            if results:
                result = results[0]
                formatted_date = format_date_br(result["payment_date"])
                net_pay = Decimal(str(result["net_pay"]))
                return (
                    f"O salário de {name if name else 'o funcionário'} referente a "
                    f"{parse_date_input(result['competency']).strftime('%b/%Y')} foi pago em "
                    f"**{formatted_date}** no valor líquido de **{format_currency(net_pay)}**. "
                    f"Fonte: `{result['employee_id']}, {result['competency']}`."
                )
            else:
                return f"Não encontrei dados de pagamento para {name} em {competency}."

        elif data_type == "bonus" and name:
            sql_query = f"""
            SELECT bonus, employee_id, competency 
            FROM payroll {where_clause}
            ORDER BY bonus DESC LIMIT 1
            """
            results = query_payroll_data(sql_query)
            if results:
                result = results[0]
                bonus = Decimal(str(result["bonus"]))
                return (
                    f"O maior bônus recebido por {name} foi de **{format_currency(result['bonus'])}** "
                    f"em {parse_date_input(result['competency']).strftime('%b/%Y')}. "
                    f"Fonte: `{result['employee_id']}, {result['competency']}`."
                )
            else:
                return f"Não encontrei dados de bônus para {name}." 
            
        elif data_type: 
            select_column = data_type          
            sql_query = f"SELECT {select_column}, employee_id, competency FROM payroll {where_clause}"
            results = query_payroll_data(sql_query)
            
            if results:
                response_parts = []
                for r in results:
                    value = r[select_column]
                    if isinstance(value, (int, float, Decimal)):
                        value = Decimal(str(value))
                        formatted_value = format_currency(value)
                    else:
                        formatted_value = value
                    if data_type == "payment_date":
                        formatted_value = format_date_br(value)
                        
                    response_parts.append(
                        f"{r['competency']}: **{formatted_value}**. "
                        f"Fonte: `{r['employee_id']}, {r['competency']}`"
                    )
                return "Os dados solicitados são:\n" + "\n".join(response_parts)
            else:
                return f"Não encontrei dados de folha de pagamento para {name} em {competency} para o item solicitado."

        elif name and competency:
            sql_query = f"SELECT * FROM payroll {where_clause}"
            results = query_payroll_data(sql_query)
            if results:
                result = results[0]
                response = (
                    f"Aqui estão os detalhes da folha de pagamento de {result['name']} em {parse_date_input(result['competency']).strftime('%b/%Y')}:\n"
                    f"- Salário Base: {format_currency(result['base_salary'])}\n"
                    f"- Bônus: {format_currency(result['bonus'])}\n"
                    f"- Líquido: {format_currency(result['net_pay'])}\n"
                    f"- INSS: {format_currency(result['deductions_inss'])}\n"
                    f"- IRRF: {format_currency(result['deductions_irrf'])}\n"
                    f"- Data de Pagamento: {parse_date_input(result['payment_date']).strftime('%d/%m/%Y')}\n"
                    f"Fonte: `{result['employee_id']}, {result['competency']}`."
                )
                return response
            else:
                return f"Não encontrei dados para {name} em {parse_date_input(competency).strftime('%b/%Y')}."
            
        return "Não consegui entender sua consulta de folha de pagamento ou faltam informações."
    
    def chat(self, user_message: str):
        """Processa a mensagem do usuário e gera uma resposta."""
        print(f"[chat] Mensagem recebida: {user_message}")
        print("[chat] Extraindo intenção e parâmetros...")
        payroll_params = self._extract_payroll_intent_and_params(user_message)
        print(f"[chat] Parâmetros extraídos: {payroll_params}")

        if payroll_params.get("intent") == "payroll_query":
            print("[chat] Processando consulta de folha de pagamento...")
            response = self._handle_payroll_query(payroll_params)
            print(f"[chat] Resposta folha de pagamento: {response}")
            self.history.append(HumanMessage(content=user_message))
            self.history.append(AIMessage(content=response))
            return response, {"source": payroll_params}
        else:
            print("[chat] Processando chat geral com LLM...")
            messages = [SystemMessage(content=self.system_prompt)] + self.history + [HumanMessage(content=user_message)]
            try:
                ai_response = self.llm.invoke(messages)
                print(f"[chat] Resposta LLM: {ai_response.content}")
                self.history.append(HumanMessage(content=user_message))
                self.history.append(AIMessage(content=ai_response.content))
                return ai_response.content, {}
            except Exception as e:
                print(f"Erro ao chamar LLM para chat geral: {e}")
                return "Desculpe, não consegui processar sua solicitação no momento. Tente novamente mais tarde.", {}