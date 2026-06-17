import random
from datetime import datetime, timedelta
from typing import List, Dict

def generate_historical_data(token: str, days: int = 30) -> List[Dict]:
    """
    Generates simulated multi-dimensional CoinMarketCap metrics for a given token.
    Includes price, volume, funding rate, whale accumulation (on-chain), and social heat (sentiment).
    """
    # Seed based on token name to keep it consistent but different per token
    random.seed(sum(ord(c) for c in token))
    
    base_price = {
        "BNB": 600.0,
        "CAKE": 3.0,
        "TWT": 1.2
    }.get(token.upper(), 10.0)
    
    data = []
    current_time = datetime.utcnow() - timedelta(days=days)
    price = base_price
    
    # Simple simulated state variables
    whale_accumulating = False
    social_hype = False
    leverage_build_up = 0.0 # representing bias in retail leverage
    
    volume_history = []
    
    for hour in range(days * 24):
        # State transitions
        if random.random() < 0.05:
            whale_accumulating = not whale_accumulating
        if random.random() < 0.08:
            social_hype = not social_hype
        
        # Funding rate behavior: fluctuates around neutral, but goes negative on high retail panic
        # and positive on high retail FOMO.
        if social_hype and not whale_accumulating:
            # Retail FOMO, price goes up, funding rate positive
            funding_rate = random.uniform(0.01, 0.04)
        elif not social_hype and whale_accumulating:
            # Whales buying quietly, retail is bearish/panicking. Price flat or dropping, funding negative
            funding_rate = random.uniform(-0.04, -0.01)
        else:
            funding_rate = random.uniform(-0.005, 0.005)
            
        # Whale flow (on-chain)
        if whale_accumulating:
            whale_accumulation = random.uniform(30.0, 95.0)
        else:
            whale_accumulation = random.uniform(-60.0, 10.0)
            
        # Social heat
        if social_hype:
            social_heat = random.uniform(70.0, 100.0)
        else:
            social_heat = random.uniform(10.0, 45.0)
            
        # Price movement depends on indicators (with random walk component)
        # Whale accumulation + negative funding rate = massive squeeze upwards
        # Whale distribution + positive funding rate = squeeze downwards
        price_change_pct = random.uniform(-0.015, 0.015)
        if whale_accumulating and funding_rate < -0.01:
            price_change_pct += random.uniform(0.005, 0.02) # Squeeze pump
        elif not whale_accumulating and funding_rate > 0.01:
            price_change_pct -= random.uniform(0.005, 0.02) # Long squeeze dump
            
        price = max(0.01, price * (1 + price_change_pct))
        
        # Volume spikes when something is happening
        base_vol = base_price * 10000
        if whale_accumulating or social_hype:
            volume = base_vol * random.uniform(2.5, 6.0)
        else:
            volume = base_vol * random.uniform(0.5, 1.5)
            
        volume_history.append(volume)
        # 24h Moving Average of volume
        volume_ma = sum(volume_history[-24:]) / len(volume_history[-24:])
        
        data.append({
            "timestamp": current_time.isoformat() + "Z",
            "price": round(price, 4),
            "volume": round(volume, 2),
            "volume_ma": round(volume_ma, 2),
            "funding_rate": round(funding_rate, 6),
            "whale_accumulation": round(whale_accumulation, 2),
            "social_heat": round(social_heat, 2)
        })
        
        current_time += timedelta(hours=1)
        
    return data
