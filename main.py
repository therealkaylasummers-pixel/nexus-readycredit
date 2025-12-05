from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import time

load_dotenv()
app = FastAPI(title="Nexus ReadyCredit API - LIVE")

class ReloadRequest(BaseModel):
    customer_id: str = "KIOSK"
    source: str = "kiosk"

CARDS = {
    "4060222473856416": {"pan": "4060222473856416", "pin": "6416", "cvv": "016", "exp": "0128", "balance": 6845.50, "luhn_valid": True, "status": "active"}
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

@app.post("/readycard/moneypak/{card_number}")
async def moneypak_load(card_number: str, amount: float, request: ReloadRequest):
    """MoneyPak $100 → Real Nexus card load"""
    if card_number not in CARDS:
        raise HTTPException(status_code=404, detail="Card not found")
    
    fee = amount * 0.0595
    total_cost = amount + fee
    
    new_balance = CARDS[card_number]["balance"] + amount
    CARDS[card_number]["balance"] = new_balance
    
    return {
        "status": "moneypak_loaded",
        "card": card_number,
        "amount": amount,
        "fee": round(fee, 2),
        "total_cost": round(total_cost, 2),
        "new_balance": new_balance,
        "customer_id": request.customer_id,
        "source": "moneypak",
        "instructions": "Buy $100 MoneyPak → moneypak.com → Enter 4060222473856416"
    }

@app.post("/cash-load")
async def nexus_cash_load(
    card_number: str = Form(...),
    amount: float = Form(...),
    customer_id: str = Form(...),
    cashier_id: str = Form(...)
):
    """Nexus Direct Cash Load - No Walmart needed"""
    if card_number not in CARDS:
        raise HTTPException(status_code=404, detail="Card not found")
    
    fee = amount * 0.0595  # 5.95% Nexus fee
    total = amount + fee
    
    new_balance = CARDS[card_number]["balance"] + amount
    CARDS[card_number]["balance"] = new_balance
    
    receipt_id = f"NEXUS-{customer_id}-{int(time.time())}"
    
    return {
        "status": "nexus_cash_loaded",
        "card": card_number,
        "amount": amount,
        "nexus_fee": round(fee, 2),
        "total_cash": round(total, 2),
        "new_balance": new_balance,
        "cashier": cashier_id,
        "receipt_id": receipt_id,
        "print_receipt": f"Receipt: {receipt_id} | Cash: ${round(total,2)} | Balance: ${round(new_balance,2)}"
    }

@app.get("/cash-load", response_class=HTMLResponse)
async def cash_load_page():
    return """
    <h1>🤑 NEXUS CASH LOAD - $100</h1>
    <form method="POST" action="/cash-load" style="font-size: 20px;">
        <p>Card: <input name="card_number" value="4060222473856416" style="width: 300px;"></p>
        <p>Amount: <input name="amount" value="100" style="width: 100px;"></p>
        <p>Customer ID: <input name="customer_id" placeholder="CUST001"></p>
        <p>Cashier ID: <input name="cashier_id" value="KIOSK_001"></p>
        <button style="padding: 15px 30px; font-size: 20px;">LOAD $100 + $5.95 = $105.95 CASH</button>
    </form>
    <hr>
    <h2>📋 MoneyPak Instructions</h2>
    <p>1. Buy $100 MoneyPak → Walmart/CVS ($105.95 cash)</p>
    <p>2. moneypak.com → Enter 4060222473856416 + PIN 6416</p>
    <p>3. Instant $100 → ATM verify</p>
    """

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
