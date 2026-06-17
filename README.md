# AlphaQuant 🚀

**AlphaQuant** is a backtestable LLM Skill that analyzes CoinMarketCap data to generate trading strategies based on volume anomalies and funding rate divergences. Built for the BNB Hack: AI Trading Agent Edition (Track 2: Strategy Skills).

## Project Overview

AlphaQuant leverages artificial intelligence and quantitative analysis to detect "smart money" accumulation (Bandarmology) in crypto markets. By processing real-time and historical data from CoinMarketCap, the Python-native agent identifies profitable entry and exit points, designed to integrate seamlessly with the official BNB AI Agent SDK.

## Strategy Spec (Volume + Funding Rate Divergence)

The core strategy revolves around two main indicators:
- **Volume Anomalies**: Sudden spikes in on-chain or exchange volume that precede price movements.
- **Funding Rate Divergence**: Identifying when perpetual futures funding rates diverge from spot price trends, indicating over-leveraged retail positions ready for a squeeze.

*See `docs/strategy_spec.md` for full details.*

## Setup Instructions

### Python Backend (FastAPI Agent)
1. Navigate to the agent directory: `cd agent`
2. Create a virtual environment (optional but recommended): `python -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the server: `uvicorn main:app --reload`
The API will be available at `http://127.0.0.1:8000`.

### Next.js Frontend (Client)
1. Navigate to the client directory: `cd client`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
The dashboard will be available at `http://localhost:3000`.

## Demo Video

[Link to Demo Video](#) (Placeholder)
