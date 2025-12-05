from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Nexus ReadyCredit API", version="1.0.0")

# Pydantic models
class ReloadRequest(BaseModel):
    customer_id: str = "KIOSK"
    source: str = "kiosk"

class CardInfo(BaseModel):
    pan: str
    pin: str
    cvv: str
    exp: str
    balance: float
    luhn_valid: bool
    status: str

# Mock data (replace with your database)
CARDS = {
    "4060222473856416": {
        "pan": "4060222473856416",
        "pin": "6416",
        "cvv": "016",
        "exp": "0128",
        "balance": 295.50,
        "luhn_valid": True,
        "status": "active"
    }
}

# Stats (replace with real analytics)
STATS = {
    "kiosks": 2000,
    "volume": 1121547,
    "cards": 8947,
    "dau": 9400000,
    "status": "✅ LIVE"
}

@app.get("/", tags=["health"])
async def root():
    return {"message": "Nexus ReadyCredit API - Cash-to-Card Kiosks LIVE", "status": "operational"}

@app.get("/dashboard", tags=["dashboard"])
async def dashboard():
    return STATS

@app.get("/readycard/balance/{card_number}", tags=["cards"])
async def get_balance(card_number: str):
    if card_number not in CARDS:
        raise HTTPException(status_code=404, detail="Card not found")
    return CARDS[card_number]

@app.post("/readycard/reload/{card_number}", tags=["cards"])
async def reload_card(card_number: str, amount: float, request: ReloadRequest):
    if card_number not in CARDS:
        raise HTTPException(status_code=404, detail="Card not found")
    
    card = CARDS[card_number]
    new_balance = card["balance"] + amount
    
    # Update balance (in production: database transaction)
    CARDS[card_number]["balance"] = new_balance
    
    return {
        "status": "success",
        "card": card_number,
        "amount": amount,
        "new_balance": new_balance,
        "customer_id": request.customer_id,
        "source": request.source,
        "timestamp": "2025-12-05T13:41:00Z"
    }

@app.get("/readycard/info/{card_number}", tags=["cards"])
async def card_info(card_number: str):
    if card_number not in CARDS:
        raise HTTPException(status_code=404, detail="Card not found")
    return CARDS[card_number]

@app.get("/mobile-app.html", tags=["kiosk"])
async def mobile_app():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Nexus ReadyCredit Kiosk</title></head>
    <body>
        <h1>🏪 Walmart Kiosk - ReadyCredit</h1>
        <p>Scan card → Insert cash → Instant load!</p>
        <script>
            // Kiosk QR code scanner integration
            fetch('/dashboard').then(r=>r.json()).then(data=>{
                document.body.innerHTML += `<p>Live: ${data.kiosks} kiosks | $${data.volume/1000}K volume</p>`;
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "nexus-readycredit"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
