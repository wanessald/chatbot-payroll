# Helper functions for formatting and parsing (in app/utils.py)
# app/utils.py
import re
from datetime import datetime

def format_currency(value):
    """Formata um valor numérico para o formato de moeda BRL."""
    if value is None:
        return "N/A"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_date_input(date_str: str):
    """Tenta parsear uma string de data/competência em um objeto datetime."""
    # Formatos esperados: YYYY-MM, YYYY-MM-DD, MM/YYYY, Mês/YYYY, Mês/YY
    formats = ["%Y-%m", "%Y-%m-%d", "%m/%Y"]
    
    # Mapeamento de meses para números
    month_map = {
        "janeiro": "01", "jan": "01", "fevereiro": "02", "fev": "02", "março": "03", "mar": "03",
        "abril": "04", "abr": "04", "maio": "05", "mai": "05", "junho": "06", "jun": "06", "julho": "07", "jul": "07",
        "agosto": "08", "ago": "08", "setembro": "09", "set": "09", "outubro": "10", "out": "10",
        "novembro": "11", "nov": "11", "dezembro": "12", "dez": "12"
    }
    
    date_str_lower = date_str.lower()
    for month_name, month_num in month_map.items():
        if month_name in date_str_lower:
            # Substitui o nome do mês pelo número para facilitar o parsing
            date_str_lower = date_str_lower.replace(month_name, month_num)
            # Tenta um formato como "01/2025" ou "2025-01"
            if re.match(r"^\d{1,2}/\d{4}$", date_str_lower):
                return datetime.strptime(date_str_lower, "%m/%Y")
            elif re.match(r"^\d{4}-\d{1,2}$", date_str_lower):
                return datetime.strptime(date_str_lower, "%Y-%m")
    
    # Tenta os formatos padrão
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    
    # Adiciona tratamento para "maio/25" -> "05/2025"
    match_short_year = re.match(r"(\w+)/(\d{2})$", date_str_lower)
    if match_short_year:
        month_part = match_short_year.group(1)
        year_part = match_short_year.group(2)
        full_year = f"20{year_part}" # Assume anos 20xx
        if month_part in month_map:
            date_str_full = f"{month_map[month_part]}/{full_year}"
            return datetime.strptime(date_str_full, "%m/%Y")

    raise ValueError(f"Formato de data '{date_str}' não reconhecido.")

def format_date_br(date_str: str) -> str:

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return date_str