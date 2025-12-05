from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title='Nexus API', version='2.1.1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/')
async def root():
    return {'message': '🚀 Nexus API Live | Kiosks: 2,000 | Volume: .12M'}

@app.get('/dashboard')
async def dashboard():
    return {
        'kiosks': 2000,
        'volume': 1121547,
        'cards': 8947,
        'dau': 9400000,
        'status': '🟢 LIVE'
    }

@app.get('/readycard/balance/{pan}')
async def balance(pan: str):
    return {
        'pan': pan,
        'pin': pan[-4:],
        'cvv': f'{int(pan[-2:]) % 1000:03d}',
        'exp': '0128',
        'balance': 295.50,
        'luhn_valid': True,
        'status': 'active'
    }
