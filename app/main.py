from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.chatbot import PayrollChatbot
from app.data_to_db import csv_to_sqlite

app = FastAPI(title="Chatbot de Folha de Pagamento")

chatbot = PayrollChatbot()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    evidence: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    print("Inicializando banco de dados de folha de pagamento...")
    csv_to_sqlite("data/payroll.csv", "data/payroll.db")
    print("Banco de dados de folha de pagamento inicializado.")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint para interagir com o chatbot."""
    try:
        response_text, evidence = chatbot.chat(request.message)
        return ChatResponse(response=response_text, evidence=evidence)
    except Exception as e:
        print(f"Erro no endpoint /chat: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    return {"status": "ok", "message": "Chatbot está funcionando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)