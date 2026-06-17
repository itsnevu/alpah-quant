from pydantic import BaseModel
from typing import List, Dict, Optional, Any
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

    def _eval_op(self, actual: float, op: str, threshold: float, ma_val: Optional[float] = None) -> bool:
        """
        Generic operator evaluator to handle various comparison types.
        """
        op = op.lower()
        if op in ["greater_than", "gt", ">"]:
            return actual > threshold
        elif op in ["less_than", "lt", "<"]:
            return actual < threshold
        elif op in ["greater_than_or_equal", "gte", ">="]:
            return actual >= threshold
        elif op in ["less_than_or_equal", "lte", "<="]:
            return actual <= threshold
        elif op in ["equal_to", "eq", "=="]:
            return actual == threshold
        elif op == "greater_than_ma_multiplier" and ma_val is not None:
            return actual > threshold * ma_val
        elif op == "less_than_ma_multiplier" and ma_val is not None:
            return actual < threshold * ma_val
        return False

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
        trades = []  # List of booleans (true = win, false = loss)
        
        for idx, bar in enumerate(historical_data):
            price = bar["price"]
            timestamp = bar["timestamp"]
            volume = bar["volume"]
            vol_ma = bar["volume_ma"]
            funding = bar["funding_rate"]
            whale = bar["whale_accumulation"]
            social = bar["social_heat"]
            
            # Map indicator names to actual metrics for generic evaluation
            metrics_map = {
                "price": price,
                "volume": volume,
                "funding_rate": funding,
                "whale_accumulation": whale,
                "social_heat": social
            }
            
            # Evaluate current equity value
            current_value = balance
            if position:
                pnl = (price - position["entry_price"]) / position["entry_price"]
                current_value = balance * (1 + pnl)
            
            # Record equity point every 12 hours + last bar
            if idx % 12 == 0 or idx == len(historical_data) - 1:
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
                    
                # Check Custom Sell/Exit Rules generically
                else:
                    sell_triggered = False
                    sell_reasons = []
                    
                    for rule in sell_rules:
                        ind = rule.get("indicator")
                        op = rule.get("operator")
                        val = rule.get("value")
                        desc = rule.get("description", "")
                        
                        if ind in metrics_map:
                            actual_val = metrics_map[ind]
                            ma_val = vol_ma if ind == "volume" else None
                            
                            if self._eval_op(actual_val, op, val, ma_val):
                                sell_triggered = True
                                rule_name = ind.replace("_", " ").title()
                                sell_reasons.append(f"{rule_name} Exit Condition ({desc or f'{op} {val}'})")
                                
                    if sell_triggered and sell_reasons:
                        balance = balance * (1 + pnl)
                        signals.append(Signal(
                            timestamp=timestamp,
                            type="SELL",
                            price=round(price, 4),
                            reason=" & ".join(sell_reasons)
                        ))
                        trades.append(pnl > 0)
                        position = None
                        
            # If not in position, check entries
            else:
                buy_triggered = True
                buy_reasons = []
                
                for rule in buy_rules:
                    ind = rule.get("indicator")
                    op = rule.get("operator")
                    val = rule.get("value")
                    desc = rule.get("description", "")
                    
                    rule_passed = False
                    if ind in metrics_map:
                        actual_val = metrics_map[ind]
                        ma_val = vol_ma if ind == "volume" else None
                        
                        if self._eval_op(actual_val, op, val, ma_val):
                            rule_passed = True
                            rule_name = ind.replace("_", " ").title()
                            
                            # Beautify display reasons
                            if ind == "volume" and op == "greater_than_ma_multiplier":
                                buy_reasons.append(f"Volume spike ({round(volume/vol_ma, 1)}x MA)")
                            elif ind == "funding_rate":
                                buy_reasons.append(f"Funding rate {actual_val} ({op} {val})")
                            else:
                                buy_reasons.append(f"{rule_name} matches ({desc or f'{op} {val}'})")
                                
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
                running_val = temp_balance * (1 + pnl) if temp_position else temp_balance
            else:
                running_val = temp_balance
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
