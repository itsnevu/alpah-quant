from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from strategy.analyzer import StrategyAnalyzer, Signal
from strategy.generator import generate_strategy_from_prompt

app = FastAPI(title="AlphaQuant API")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for easier local hackathon testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Metrics(BaseModel):
    roi: str
    winRate: str
    maxDrawdown: str

class EquityPoint(BaseModel):
    timestamp: str
    value: float

class BacktestResult(BaseModel):
    metrics: Metrics
    signals: List[Signal]
    equity: List[EquityPoint]

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/api/generate-strategy")
async def generate_strategy(req: GenerateRequest):
    """
    Parses a natural language prompt into a quantitative strategy spec.
    """
    spec = generate_strategy_from_prompt(req.prompt)
    return spec

@app.post("/api/backtest", response_model=BacktestResult)
async def post_backtest(spec: Dict[str, Any]):
    """
    Executes a backtest on a structured strategy spec.
    """
    analyzer = StrategyAnalyzer()
    results = analyzer.run_backtest(spec)
    return results

@app.get("/api/backtest", response_model=BacktestResult)
async def get_backtest():
    """
    Default backtest for first-page load.
    """
    default_spec = {
        "token": "BNB",
        "name": "Volume & Funding Divergence (Default)",
        "indicators_used": ["volume", "funding_rate"],
        "buy_rules": [
            {
                "indicator": "volume",
                "operator": "greater_than_ma_multiplier",
                "value": 2.5,
                "description": "Volume spike > 2.5x MA"
            },
            {
                "indicator": "funding_rate",
                "operator": "less_than",
                "value": -0.005,
                "description": "Negative funding rate indicating panic"
            }
        ],
        "sell_rules": [
            {
                "indicator": "funding_rate",
                "operator": "greater_than",
                "value": 0.015,
                "description": "Positive funding rate indicating FOMO"
            }
        ],
        "risk_management": {
            "take_profit_pct": 5.0,
            "stop_loss_pct": 2.0,
            "trailing_stop_pct": 1.0
        }
    }
    
    analyzer = StrategyAnalyzer()
    results = analyzer.run_backtest(default_spec)
    return results
