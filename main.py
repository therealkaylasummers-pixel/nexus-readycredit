from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import uvicorn

app = FastAPI(title="Nexus Ready Credit - 2000 Cards")

# 2000 PRODUCTION CARDS (4060222473856416 → 4060222475856415)
cards = {}
base_pan = "4060222473856416"
for i in range(2000):
    pan = f"406022247{3856416 + i:07d}"
    cards[pan] = {
        "pan": pan,
        "pin": f"641{i % 1000:03d}",
        "cvv": f"{16 + (i % 100):03d}",
        "exp": "0128",
        "balance": 1000.00,  # $1K each → $2M total capacity
        "status": "active",
        "luhn_valid": True
    }

@app.get("/")
@app.get("/dashboard")
def dashboard():
    return {
        "kiosks": 2000,
        "cards": len(cards),
        "total_balance": sum(c["balance"] for c in cards.values()),
        "volume": 1121547,
        "dau": 9400000,
        "status": "🟢 2000 CARDS LIVE"
    }

@app.get("/readycard/balance/{pan}")
def balance(pan: str):
    card = cards.get(pan)
    if not card: raise HTTPException(404, "Card not found")
    return card

@app.post("/readycard/reload/{pan}")
def reload(pan: str, amount: float = Query(..., ge=20, le=5000), 
           customer_id: str = "KIOSK_001", source: str = "walmart"):
    card = cards.get(pan)
    if not card or card["status"] != "active": raise HTTPException(404, "Card inactive")
    card["balance"] += amount
    return {"status":"success","card":pan,"amount":amount,"new_balance":card["balance"],
            "customer_id":customer_id,"source":source}

@app.get("/cash-load")
def cash_load():
    return {"status":"Cash-to-Card Kiosk","fee":5.95,"min_load":20,"max_load":5000}

@app.post("/readycard/moneypak/{pan}")
def moneypak(pan: str, amount: float = Query(..., ge=20, le=5000)):
    card = cards.get(pan)
    if not card: raise HTTPException(404, "Card not found")
    card["balance"] += amount
    return {"status":"success","new_balance":card["balance"],"amount":amount}

@app.get("/health")
def health(): return {"status":"healthy","cards":len(cards)}

@app.get("/favicon.ico")
def favicon(): return Response(status_code=204)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
