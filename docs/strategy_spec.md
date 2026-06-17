# Quantitative Strategy Specification: AlphaQuant

## Core Concept: Bandarmology & Smart Money Detection

The strategy is built on the premise that "smart money" (whales, institutional investors) leaves footprints in the form of volume anomalies and funding rate divergences before major price movements. This is often referred to as "Bandarmology" in certain trading circles.

### 1. Volume Anomalies
We track abnormal spikes in trading volume that occur with minimal price movement. This often indicates accumulation (buying) or distribution (selling) by large entities masking their activity.
- **Trigger**: 5-minute volume > 3x the 24-hour moving average volume.

### 2. Funding Rate Divergence
We analyze perpetual futures funding rates across major exchanges (via CoinMarketCap API).
- **Bullish Divergence**: Price is consolidating/dropping, but funding rates are deeply negative (retail is aggressively shorting).
- **Bearish Divergence**: Price is consolidating/rising, but funding rates are highly positive (retail is aggressively longing).

## Entry Rules
- **Long**: Volume Anomaly (Accumulation) + Negative Funding Rate Divergence.
- **Short**: Volume Anomaly (Distribution) + Positive Funding Rate Divergence.

## Exit Rules & Risk Management
- **Take Profit (TP)**: Dynamic TP based on 2x Average True Range (ATR).
- **Stop Loss (SL)**: 1% hard stop loss from entry price.
- **Trailing Stop**: Activate trailing stop of 0.5% once the trade is 1% in profit to protect gains.
