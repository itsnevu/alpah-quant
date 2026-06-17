# AlphaQuant AI 🚀

**AlphaQuant AI** is a state-of-the-art AI-native quantitative trading strategy generator and backtester built for the **BNB Hack: AI Trading Agent Edition (Track 2: Strategy Skills)**. 

Instead of hardcoding a single trading strategy, AlphaQuant AI provides a **Quantopian-style natural language interface** powered by **OpenRouter (Step-3.5 Flash)**. It translates freeform prompts into structured, backtestable quant strategy specifications, evaluates them dynamically against multi-dimensional market metrics, and outputs clean visual results.

---

## 🌟 Key Features

1. **Natural Language Strategy Compiler**: Write strategy ideas in plain English or Indonesian (e.g., *"Beli CAKE jika whale accumulation > 30 dan funding rate negatif, exit jika social heat > 80"*). The LLM compiles it into a structured JSON trading specification.
2. **Multi-Dimensional CMC Metrics Engine**: Simulates and evaluates strategies against 30 days of hourly CoinMarketCap-style data:
   * **Derivatives**: Perpetual futures funding rates.
   * **On-Chain**: Whale net inflows/outflows (accumulation score).
   * **Social**: Sentiment score and KOL hype indicators.
   * **Volume**: Price & volume anomalies (moving average multipliers).
3. **Dynamic Quant Backtester**: Calculates realistic trading performance metrics:
   * Estimated Return on Investment (ROI)
   * Trade Win Rate
   * Max Drawdown (risk guard)
   * Log of detailed Buy/Sell signals with execution reasoning.
4. **Premium Visual Terminal**: Sleek dark-mode glassmorphic dashboard featuring:
   * **Dynamic logs terminal** showing compilation processes.
   * **Modern AreaChart** with emerald gradients to plot the portfolio equity curve.
   * **One-click presets** for instant testing.
5. **Trust Wallet Agent Kit (TWAK) Exporter**: Download the compiled strategy spec as a clean JSON configuration ready to be loaded by TWAK for autonomous live execution.

---

## 🛠️ Tech Stack

* **Frontend**: Next.js 14, React 18, Tailwind CSS, Recharts (AreaChart)
* **Backend**: FastAPI, Uvicorn, Python-dotenv
* **LLM Engine**: OpenRouter API (`stepfun/step-3.5-flash` or `anthropic/claude-3.5-sonnet`) with Gemini API as fallback

---

## 🚀 Setup & Execution Instructions

### 🐍 1. Backend Setup (FastAPI Agent)

1. Navigate to the agent directory:
   ```bash
   cd agent
   ```
2. Create and activate a virtual environment:
   * **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **macOS/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your environment variables:
   * Copy the template file:
     ```bash
     cp .env.example .env
     ```
   * Open `.env` and fill in your OpenRouter API Key:
     ```env
     OPENROUTER_API_KEY=your_openrouter_api_key_here
     OPENROUTER_MODEL=stepfun/step-3.5-flash
     ```
5. Run the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```
   * *The API will be live at `http://127.0.0.1:8000`.*

---

### 🌐 2. Frontend Setup (Next.js Dashboard)

1. Navigate to the client directory:
   ```bash
   cd client
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   * *Open your browser and navigate to **`http://localhost:3000`**.*

---

## 📁 Project Structure

```
alpha-quant/
├── agent/                  # FastAPI Backend
│   ├── strategy/
│   │   ├── dataset.py      # Simulated multi-dimensional CMC metric generator
│   │   ├── generator.py    # LLM Prompt strategy parser (OpenRouter/Gemini)
│   │   └── analyzer.py     # Generic quant backtest evaluation engine
│   ├── main.py             # API endpoints and startup logic
│   └── requirements.txt    # Backend dependencies
├── client/                 # Next.js Frontend
│   ├── app/
│   │   ├── globals.css     # Premium dark theme and glow keyframes
│   │   └── page.tsx        # Terminal UI, preset cards, logs, tab manager
│   └── components/
│   │   └── BacktestChart.tsx # Recharts emerald area curve visualization
└── docs/
    └── strategy_spec.md    # Original concept description
```
