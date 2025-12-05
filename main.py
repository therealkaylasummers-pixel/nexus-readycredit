from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Nexus ReadyCredit API")

class ReloadRequest(BaseModel):
    customer_id: str = "KIOSK"
    source: str = "kiosk"

CARDS = {
    "4060222473856416": {"pan": "4060222473856416", "pin": "6416", "cvv": "016", "exp": "0128", "balance": 295.50, "luhn_valid": True, "status": "active"}
}

STATS = {"kiosks": 2000, "volume": 1121547, "cards": 8947, "dau": 9400000, "status": "✅ LIVE"}

@app.get("/")
async def root():
    return {"message": "Nexus ReadyCredit API - LIVE"}

@app.get("/dashboard")
async def dashboard():
    return STATS

@app.get("/readycard/balance/{card_number}")
async def get_balance(card_number: str):
    if card_number not in CARDS:
        raise HTTPException(status_code=404, detail="Card not found")
    return CARDS[card_number]

@app.post("/readycard/reload/{card_number}")
async def reload_card(card_number: str, amount: float, request: ReloadRequest):
    if card_number not in CARDS:
        raise HTTPException(status_code=404, detail="Card not found")
    
    card = CARDS[card_number]
    new_balance = card["balance"] + amount
    CARDS[card_number]["balance"] = new_balance
    
    return {
        "status": "success",
        "card": card_number,
        "amount": amount,
        "new_balance": new_balance,
        "customer_id": request.customer_id,
        "source": request.source
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
