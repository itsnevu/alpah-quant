from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from strategy.dataset import generate_historical_data

class Signal(BaseModel):
    timestamp: str
    type: str  # BUY, SELL, HOLD, EXIT
    price: float
    reason: str

class StrategyAnalyzer:
    """
    Core quant engine that parses a strategy spec and runs a backtest
    against simulated multi-dimensional CoinMarketCap metrics.
    """
    def __init__(self):
        pass

    def run_backtest(self, spec: Dict) -> Dict:
        token = spec.get("token", "BNB")
        buy_rules = spec.get("buy_rules", [])
        sell_rules = spec.get("sell_rules", [])
        risk = spec.get("risk_management", {})
        
        tp_pct = risk.get("take_profit_pct", 5.0) / 100.0
        sl_pct = risk.get("stop_loss_pct", 2.0) / 100.0
        ts_pct = risk.get("trailing_stop_pct", 1.0) / 100.0
        
        # Fetch mock CMC historical dataset
        historical_data = generate_historical_data(token, days=30)
        
        initial_balance = 10000.0
        balance = initial_balance
        position = None  # None or {"entry_price": float, "type": "LONG", "highest_price": float}
        
        signals = []
        equity_curve = []
        trades = []  # List of dicts to track win/loss
        
        for idx, bar in enumerate(historical_data):
            price = bar["price"]
            timestamp = bar["timestamp"]
            volume = bar["volume"]
            vol_ma = bar["volume_ma"]
            funding = bar["funding_rate"]
            whale = bar["whale_accumulation"]
            social = bar["social_heat"]
            
            # Evaluate current equity value
            current_value = balance
            if position:
                pnl = (price - position["entry_price"]) / position["entry_price"]
                current_value = balance * (1 + pnl)
            
            # Record daily or interval equity point (let's do every 12 hours to keep data size reasonable)
            if idx % 12 == 0 or idx == len(historical_data) - 1:
                # Format to short date
                date_str = timestamp.split("T")[0] + " " + timestamp.split("T")[1][:5]
                equity_curve.append({
                    "timestamp": date_str,
                    "value": round(current_value, 2)
                })
                
            # If in position, check exits
            if position:
                pnl = (price - position["entry_price"]) / position["entry_price"]
                
                # Update peak price for trailing stop
                if price > position["highest_price"]:
                    position["highest_price"] = price
                
                trailing_trigger = position["highest_price"] * (1 - ts_pct)
                
                # Check Stop Loss
                if pnl <= -sl_pct:
                    # SL Triggered
                    balance = balance * (1 - sl_pct)
                    signals.append(Signal(
                        timestamp=timestamp,
                        type="SELL",
                        price=round(price, 4),
                        reason=f"Stop Loss Triggered at -{sl_pct*100}%"
                    ))
                    trades.append(False)
                    position = None
                # Check Take Profit
                elif pnl >= tp_pct:
                    balance = balance * (1 + tp_pct)
                    signals.append(Signal(
                        timestamp=timestamp,
                        type="SELL",
                        price=round(price, 4),
                        reason=f"Take Profit Triggered at +{tp_pct*100}%"
                    ))
                    trades.append(True)
                    position = None
                # Check Trailing Stop
                elif price <= trailing_trigger and pnl > 0:
                    exit_pnl = (trailing_trigger - position["entry_price"]) / position["entry_price"]
                    balance = balance * (1 + exit_pnl)
                    signals.append(Signal(
                        timestamp=timestamp,
                        type="SELL",
                        price=round(trailing_trigger, 4),
                        reason=f"Trailing Stop Triggered at +{round(exit_pnl*100, 2)}%"
                    ))
                    trades.append(exit_pnl > 0)
                    position = None
                # Check Sell Rules
                else:
                    sell_triggered = False
                    sell_reason = ""
                    for rule in sell_rules:
                        ind = rule["indicator"]
                        op = rule["operator"]
                        val = rule["value"]
                        desc = rule.get("description", "")
                        
                        if ind == "funding_rate":
                            if op == "greater_than" and funding > val:
                                sell_triggered = True
                                sell_reason = f"Sell Rule: Funding {funding} > {val} ({desc})"
                            elif op == "less_than" and funding < val:
                                sell_triggered = True
                                sell_reason = f"Sell Rule: Funding {funding} < {val} ({desc})"
                        elif ind == "whale_accumulation":
                            if op == "greater_than" and whale > val:
                                sell_triggered = True
                                sell_reason = f"Sell Rule: Whale Accumulation {whale} > {val} ({desc})"
                            elif op == "less_than" and whale < val:
                                sell_triggered = True
                                sell_reason = f"Sell Rule: Whale Accumulation {whale} < {val} ({desc})"
                                
                    if sell_triggered:
                        balance = balance * (1 + pnl)
                        signals.append(Signal(
                            timestamp=timestamp,
                            type="SELL",
                            price=round(price, 4),
                            reason=sell_reason
                        ))
                        trades.append(pnl > 0)
                        position = None
                        
            # If not in position, check entries
            else:
                buy_triggered = True
                buy_reasons = []
                
                for rule in buy_rules:
                    ind = rule["indicator"]
                    op = rule["operator"]
                    val = rule["value"]
                    desc = rule.get("description", "")
                    
                    rule_passed = False
                    
                    if ind == "volume":
                        if op == "greater_than_ma_multiplier":
                            if volume > val * vol_ma:
                                rule_passed = True
                                buy_reasons.append(f"Volume spike ({round(volume/vol_ma, 1)}x MA)")
                        elif op == "greater_than" and volume > val:
                            rule_passed = True
                            buy_reasons.append(f"Volume {volume} > {val}")
                            
                    elif ind == "funding_rate":
                        if op == "less_than" and funding < val:
                            rule_passed = True
                            buy_reasons.append(f"Funding {funding} < {val}")
                        elif op == "greater_than" and funding > val:
                            rule_passed = True
                            buy_reasons.append(f"Funding {funding} > {val}")
                            
                    elif ind == "whale_accumulation":
                        if op == "greater_than" and whale > val:
                            rule_passed = True
                            buy_reasons.append(f"Whale flow {whale} > {val}")
                        elif op == "less_than" and whale < val:
                            rule_passed = True
                            buy_reasons.append(f"Whale flow {whale} < {val}")
                            
                    elif ind == "social_heat":
                        if op == "greater_than" and social > val:
                            rule_passed = True
                            buy_reasons.append(f"Social heat {social} > {val}")
                        elif op == "less_than" and social < val:
                            rule_passed = True
                            buy_reasons.append(f"Social heat {social} < {val}")
                            
                    if not rule_passed:
                        buy_triggered = False
                        break
                        
                if buy_triggered and buy_rules:
                    position = {
                        "entry_price": price,
                        "type": "LONG",
                        "highest_price": price
                    }
                    signals.append(Signal(
                        timestamp=timestamp,
                        type="BUY",
                        price=round(price, 4),
                        reason=" & ".join(buy_reasons)
                    ))
                    
        # Calculate final performance
        final_equity = balance
        if position:
            last_price = historical_data[-1]["price"]
            pnl = (last_price - position["entry_price"]) / position["entry_price"]
            final_equity = balance * (1 + pnl)
            
        roi = ((final_equity - initial_equity) / initial_equity) * 100
        win_rate = (sum(1 for t in trades if t) / len(trades) * 100) if trades else 0.0
        
        # Max Drawdown calculation
        peak = initial_equity
        max_dd = 0.0
        running_equity = initial_equity
        pos_entry_idx = None
        
        # Re-traverse equity steps to find max drawdown
        temp_balance = initial_equity
        temp_position = None
        
        for idx, bar in enumerate(historical_data):
            p = bar["price"]
            if temp_position:
                pnl = (p - temp_position["entry_price"]) / temp_position["entry_price"]
                # SL or TP check simulation
                if pnl <= -sl_pct:
                    temp_balance *= (1 - sl_pct)
                    temp_position = None
                elif pnl >= tp_pct:
                    temp_balance *= (1 + tp_pct)
                    temp_position = None
                # Update peak for current trade
                # Simple approximation
                running_val = temp_balance * (1 + pnl) if temp_position else temp_balance
            else:
                running_val = temp_balance
                # Trigger entry check (simplified matching the signal logs)
                matching_buy = [s for s in signals if s.timestamp == bar["timestamp"] and s.type == "BUY"]
                if matching_buy:
                    temp_position = {"entry_price": p}
                    
            if running_val > peak:
                peak = running_val
            dd = (peak - running_val) / peak * 100
            if dd > max_dd:
                max_dd = dd
                
        return {
            "metrics": {
                "roi": f"{'+' if roi >= 0 else ''}{round(roi, 1)}%",
                "winRate": f"{round(win_rate, 0)}%",
                "maxDrawdown": f"-{round(max_dd, 1)}%"
            },
            "signals": signals,
            "equity": equity_curve
        }
