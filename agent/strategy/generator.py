import os
import json
import re
from typing import Dict

def generate_strategy_from_prompt(prompt: str) -> Dict:
    """
    Parses a natural language prompt into a structured, backtestable trading strategy spec.
    First tries to use LLM via Gemini (if API key is present), otherwise falls back to a 
    powerful semantic heuristic parser.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            # We could call Gemini using a simple requests call to keep things light 
            # and avoid heavy dependencies
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            system_instruction = (
                "You are an expert quantitative trading developer. Parse the user's trading strategy prompt "
                "into a JSON spec. You must ONLY output valid JSON. Do not write anything else. "
                "Structure of JSON:\n"
                "{\n"
                "  \"token\": \"BNB\" | \"CAKE\" | \"TWT\" (default to BNB),\n"
                "  \"name\": \"Name of strategy\",\n"
                "  \"indicators_used\": [\"volume\", \"funding_rate\", \"whale_accumulation\", \"social_heat\"],\n"
                "  \"buy_rules\": [\n"
                "    { \"indicator\": \"indicator_name\", \"operator\": \"less_than\"|\"greater_than\", \"value\": float_value, \"description\": \"text description\" }\n"
                "  ],\n"
                "  \"sell_rules\": [\n"
                "    { \"indicator\": \"indicator_name\", \"operator\": \"less_than\"|\"greater_than\", \"value\": float_value, \"description\": \"text description\" }\n"
                "  ],\n"
                "  \"risk_management\": {\n"
                "    \"take_profit_pct\": float,\n"
                "    \"stop_loss_pct\": float,\n"
                "    \"trailing_stop_pct\": float\n"
                "  }\n"
                "}"
            )
            
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_instruction}\n\nPrompt: {prompt}"}]}
                ]
            }
            
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                result_json = res.json()
                text_out = result_json["candidates"][0]["content"]["parts"][0]["text"]
                # Clean code blocks
                text_cleaned = re.sub(r"```json\s*", "", text_out)
                text_cleaned = re.sub(r"```\s*$", "", text_cleaned).strip()
                return json.loads(text_cleaned)
        except Exception as e:
            print(f"Gemini API call failed, falling back to heuristic parser: {e}")
            
    # Fallback Heuristic Parser
    prompt_lower = prompt.lower()
    
    # Token determination
    token = "BNB"
    if "cake" in prompt_lower:
        token = "CAKE"
    elif "twt" in prompt_lower or "trust" in prompt_lower:
        token = "TWT"
        
    # Default Risk Settings
    tp = 5.0
    sl = 2.0
    ts = 1.0
    if "agresif" in prompt_lower or "aggressive" in prompt_lower or "high risk" in prompt_lower:
        tp = 8.0
        sl = 3.0
        ts = 1.5
    elif "defensif" in prompt_lower or "conservative" in prompt_lower or "low risk" in prompt_lower:
        tp = 3.0
        sl = 1.0
        ts = 0.5
        
    indicators = []
    buy_rules = []
    sell_rules = []
    
    # Check volume keywords
    if any(k in prompt_lower for k in ["volume", "volume anomaly", "akumulasi", "accumulation", "spike"]):
        indicators.append("volume")
        buy_rules.append({
            "indicator": "volume",
            "operator": "greater_than_ma_multiplier",
            "value": 2.5,
            "description": "Volume is greater than 2.5x of the 24-hour moving average volume"
        })
        
    # Check funding rate keywords
    if "funding" in prompt_lower or "perpetual" in prompt_lower or "short" in prompt_lower or "long" in prompt_lower:
        indicators.append("funding_rate")
        if any(k in prompt_lower for k in ["negatif", "negative", "short", "divergence"]):
            buy_rules.append({
                "indicator": "funding_rate",
                "operator": "less_than",
                "value": -0.005,
                "description": "Funding rate is negative (retail is shorting aggressively)"
            })
        if any(k in prompt_lower for k in ["positif", "positive", "long"]):
            sell_rules.append({
                "indicator": "funding_rate",
                "operator": "greater_than",
                "value": 0.01,
                "description": "Funding rate is positive (retail is over-leveraged long)"
            })
            
    # Check on-chain whale flow keywords
    if any(k in prompt_lower for k in ["whale", "on-chain", "bandar", "flow", "accumulation"]):
        indicators.append("whale_accumulation")
        buy_rules.append({
            "indicator": "whale_accumulation",
            "operator": "greater_than",
            "value": 30.0,
            "description": "Whale net accumulation score is positive (>30)"
        })
        sell_rules.append({
            "indicator": "whale_accumulation",
            "operator": "less_than",
            "value": -30.0,
            "description": "Whale net distribution score is negative (<-30)"
        })
        
    # Check social / hype keywords
    if any(k in prompt_lower for k in ["social", "hype", "sentimen", "sentiment", "heat", "twitter", "kol"]):
        indicators.append("social_heat")
        if "hype" in prompt_lower or "heat" in prompt_lower or "naik" in prompt_lower or "high" in prompt_lower:
            buy_rules.append({
                "indicator": "social_heat",
                "operator": "greater_than",
                "value": 75.0,
                "description": "Social heat and community interest is very high (>75)"
            })
        if "fud" in prompt_lower or "down" in prompt_lower or "panik" in prompt_lower or "panic" in prompt_lower:
            buy_rules.append({
                "indicator": "social_heat",
                "operator": "less_than",
                "value": 25.0,
                "description": "Social sentiment is in extreme fear/fud zone (<25)"
            })
            
    # Fallback to standard momentum / default if no rules detected
    if not buy_rules:
        indicators = ["volume", "funding_rate"]
        buy_rules = [
            {
                "indicator": "volume",
                "operator": "greater_than_ma_multiplier",
                "value": 2.0,
                "description": "Volume spike above 2x MA"
            },
            {
                "indicator": "funding_rate",
                "operator": "less_than",
                "value": -0.002,
                "description": "Negative funding rate indicating retail shorts"
            }
        ]
        sell_rules = [
            {
                "indicator": "funding_rate",
                "operator": "greater_than",
                "value": 0.015,
                "description": "Positive funding rate indicating retail longs"
            }
        ]
        
    # Keep indicators unique
    indicators = list(set(indicators))
    if not indicators:
        indicators = ["volume"]
        
    # Build strategy name
    name = "Custom AlphaQuant Strategy"
    if "momentum" in prompt_lower:
        name = "AlphaQuant Momentum Squeeze"
    elif "whale" in prompt_lower or "bandar" in prompt_lower:
        name = "AlphaQuant Smart Money Accumulation"
    elif "sentimen" in prompt_lower or "sentiment" in prompt_lower:
        name = "AlphaQuant Sentiment Divergence"
        
    return {
        "token": token,
        "name": name,
        "indicators_used": indicators,
        "buy_rules": buy_rules,
        "sell_rules": sell_rules,
        "risk_management": {
            "take_profit_pct": tp,
            "stop_loss_pct": sl,
            "trailing_stop_pct": ts
        }
    }
