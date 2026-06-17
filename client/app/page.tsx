"use client";

import { useEffect, useState } from "react";
import BacktestChart from "../components/BacktestChart";

interface Rule {
  indicator: string;
  operator: string;
  value: number;
  description: string;
}

interface RiskManagement {
  take_profit_pct: number;
  stop_loss_pct: number;
  trailing_stop_pct: number;
}

interface StrategySpec {
  token: string;
  name: string;
  indicators_used: string[];
  buy_rules: Rule[];
  sell_rules: Rule[];
  risk_management: RiskManagement;
}

interface Metrics {
  roi: string;
  winRate: string;
  maxDrawdown: string;
  sharpeRatio: string;
  profitFactor: string;
  totalTrades: string;
  feesPaid: string;
}

interface Signal {
  timestamp: string;
  type: string;
  price: number;
  reason: string;
}

interface BacktestData {
  metrics: Metrics;
  signals: Signal[];
  equity: { timestamp: string; value: number }[];
}

export default function Home() {
  const [prompt, setPrompt] = useState(
    "Buat strategi akumulasi jika volume naik 2x lipat dan funding rate negatif, exit jika funding rate naik di atas 1.5%."
  );
  const [spec, setSpec] = useState<StrategySpec | null>(null);
  const [data, setData] = useState<BacktestData | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"chart" | "spec" | "signals">("chart");

  const presets = [
    {
      title: "🐳 Whale Accumulation & Squeeze",
      prompt: "Buat strategi untuk koin CAKE yang mendeteksi akumulasi whale (>30 score) dengan funding rate negatif (< -0.005) saat retail panik.",
      label: "Whale Focus"
    },
    {
      title: "🔥 Sentiment Divergence Hype",
      prompt: "Beli token BNB ketika social heat melonjak tinggi (>75 score) dan whale akumulasi positif, exit saat funding rate terlalu positif (>0.02).",
      label: "Social Hype"
    },
    {
      title: "🛡️ Conservative Momentum",
      prompt: "Strategi defensif untuk TWT dengan volume spike 3x lipat, stop loss ketat 1%, take profit 3%.",
      label: "Defensive"
    }
  ];

  // Perform initial default backtest loading
  useEffect(() => {
    setLoading(true);
    setLogs(["[SYSTEM] Connecting to AlphaQuant API...", "[SYSTEM] Loading default strategy..."]);
    
    fetch("http://127.0.0.1:8000/api/backtest")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        // Default Spec structure matching default GET endpoint
        setSpec({
          token: "BNB",
          name: "Volume & Funding Divergence (Default)",
          indicators_used: ["volume", "funding_rate"],
          buy_rules: [
            { indicator: "volume", operator: "greater_than_ma_multiplier", value: 2.5, description: "Volume spike > 2.5x MA" },
            { indicator: "funding_rate", operator: "less_than", value: -0.005, description: "Negative funding rate indicating panic" }
          ],
          sell_rules: [
            { indicator: "funding_rate", operator: "greater_than", value: 0.015, description: "Positive funding rate indicating FOMO" }
          ],
          risk_management: { take_profit_pct: 5.0, stop_loss_pct: 2.0, trailing_stop_pct: 1.0 }
        });
        setLogs((prev) => [
          ...prev,
          "[SUCCESS] Connected to API.",
          "[SUCCESS] Loaded default backtest successfully."
        ]);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch default backtest:", err);
        setLogs((prev) => [
          ...prev,
          "[ERROR] Failed to fetch. Make sure FastAPI backend is running on http://127.0.0.1:8000"
        ]);
        setLoading(false);
      });
  }, []);

  const handleCompileAndBacktest = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setLogs(["[LLM] Analyzing natural language strategy prompt...", `[PROMPT] "${prompt}"`]);

    try {
      // Step 1: Generate Strategy Spec
      const genRes = await fetch("http://127.0.0.1:8000/api/generate-strategy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const generatedSpec: StrategySpec = await genRes.json();
      setSpec(generatedSpec);
      
      setLogs((prev) => [
        ...prev,
        `[SUCCESS] Strategy generated: "${generatedSpec.name}" for token ${generatedSpec.token}`,
        `[INFO] Target Indicators: ${generatedSpec.indicators_used.join(", ")}`,
        `[INFO] Risk Settings: TP: ${generatedSpec.risk_management.take_profit_pct}%, SL: ${generatedSpec.risk_management.stop_loss_pct}%, Trailing Stop: ${generatedSpec.risk_management.trailing_stop_pct}%`,
        `[SYSTEM] Invoking CoinMarketCap Agent Hub data engine...`,
        `[SYSTEM] Pulling multi-dimensional historical dataset for ${generatedSpec.token}...`,
        `[SYSTEM] Starting quant backtest engine over 30 days of data...`
      ]);

      // Step 2: Backtest Strategy Spec
      const backtestRes = await fetch("http://127.0.0.1:8000/api/backtest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(generatedSpec),
      });
      const backtestData: BacktestData = await backtestRes.json();
      setData(backtestData);

      setLogs((prev) => [
        ...prev,
        `[SUCCESS] Backtest completed!`,
        `[METRICS] ROI: ${backtestData.metrics.roi} | Win Rate: ${backtestData.metrics.winRate} | Drawdown: ${backtestData.metrics.maxDrawdown}`,
        `[METRICS] Total Signals generated: ${backtestData.signals.length}`
      ]);
    } catch (error) {
      console.error("Backtest flow failed:", error);
      setLogs((prev) => [...prev, "[ERROR] Compilation or Backtest execution failed. See console."]);
    } finally {
      setLoading(false);
    }
  };

  const handleExportTWAK = () => {
    if (!spec) return;
    const jsonStr = JSON.stringify(spec, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `twak_strategy_${spec.token.toLowerCase()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <main className="min-h-screen bg-black text-gray-100 p-6 relative overflow-hidden font-sans">
      {/* Visual Ambient Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] animate-pulse-glow" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] animate-pulse-glow" style={{ animationDelay: "1.5s" }} />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 pb-6 border-b border-gray-800/80">
          <div>
            <div className="flex items-center gap-2">
              <span className="bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs px-2.5 py-1 rounded-full font-semibold uppercase tracking-wider">
                Track 2: Strategy Skills
              </span>
              <span className="bg-gray-800 text-gray-300 text-xs px-2.5 py-1 rounded-full font-mono">
                v1.2.0
              </span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight mt-3 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-indigo-400">
              AlphaQuant AI Terminal
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Natural Language Strategy Generator & Dynamic Backtester powered by CoinMarketCap Agent Hub
            </p>
          </div>
          <div className="mt-4 md:mt-0 flex gap-3">
            <button
              onClick={handleExportTWAK}
              disabled={!spec}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-gray-900 border border-gray-700 hover:border-gray-500 hover:bg-gray-800 text-gray-200 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              📥 Export TWAK Config
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Panel: Prompt Input, Presets & Build logs (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            {/* Prompt Area */}
            <div className="glass-panel p-6 rounded-2xl shadow-xl flex flex-col gap-4">
              <h2 className="text-sm font-semibold tracking-wider text-emerald-400 uppercase">
                1. Author Trading Strategy
              </h2>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Tuliskan logika strategi trading Anda di sini..."
                className="w-full h-36 bg-gray-950/70 border border-gray-800 focus:border-emerald-500/60 rounded-xl p-4 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500/50 resize-none text-gray-200 font-sans transition-all placeholder:text-gray-600"
              />
              
              {/* Presets */}
              <div className="flex flex-col gap-2">
                <span className="text-xs font-semibold text-gray-500">Presets & Examples:</span>
                <div className="flex flex-col gap-2">
                  {presets.map((preset, idx) => (
                    <button
                      key={idx}
                      onClick={() => setPrompt(preset.prompt)}
                      className="text-left bg-gray-900/40 hover:bg-emerald-950/20 border border-gray-800 hover:border-emerald-500/30 p-2.5 rounded-lg transition-all group"
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-semibold text-gray-300 group-hover:text-emerald-400 transition-colors">
                          {preset.title}
                        </span>
                        <span className="text-[10px] bg-gray-800 text-gray-400 px-1.5 py-0.5 rounded uppercase font-bold">
                          {preset.label}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={handleCompileAndBacktest}
                disabled={loading}
                className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-black font-bold py-3 rounded-xl transition-all duration-300 shadow-lg shadow-emerald-500/20 hover:shadow-emerald-400/35 transform hover:-translate-y-0.5 flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-black border-t-transparent" />
                    Compiling Strategy...
                  </>
                ) : (
                  <>⚡ Compile & Run Backtest</>
                )}
              </button>
            </div>

            {/* Build Log Terminal */}
            <div className="glass-panel p-6 rounded-2xl flex flex-col h-[280px]">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  Terminal Logs
                </h2>
                <button
                  onClick={() => setLogs([])}
                  className="text-[10px] text-gray-500 hover:text-gray-300 transition-colors"
                >
                  Clear
                </button>
              </div>
              <div className="bg-gray-950/90 border border-gray-800 rounded-xl p-4 font-mono text-xs overflow-y-auto flex-1 flex flex-col gap-1.5 text-emerald-500/90">
                {logs.map((log, idx) => {
                  let color = "text-gray-400";
                  if (log.startsWith("[SUCCESS]")) color = "text-emerald-400 font-semibold";
                  if (log.startsWith("[ERROR]")) color = "text-red-400 font-semibold";
                  if (log.startsWith("[LLM]")) color = "text-indigo-400";
                  if (log.startsWith("[METRICS]")) color = "text-amber-400";
                  return (
                    <div key={idx} className={`${color} leading-relaxed break-words`}>
                      {log}
                    </div>
                  );
                })}
                {loading && (
                  <div className="text-gray-500 animate-pulse">Running compilation processes...</div>
                )}
                {logs.length === 0 && (
                  <div className="text-gray-600 italic">No logs generated yet. Compile a strategy to begin.</div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel: Metrics, Chart & Tabs (7 cols) */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            {/* Top Metrics Cards */}
            {data && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass-panel-emerald p-4 rounded-xl flex flex-col border-emerald-500/20 shadow-lg shadow-emerald-500/5 hover:-translate-y-0.5 transition-all">
                  <span className="text-[10px] uppercase font-bold text-emerald-500 tracking-wider">Estimated ROI</span>
                  <span className="text-2xl font-extrabold text-emerald-400 mt-1">{data.metrics.roi}</span>
                </div>
                <div className="glass-panel p-4 rounded-xl flex flex-col hover:-translate-y-0.5 transition-all">
                  <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Win Rate</span>
                  <span className="text-2xl font-extrabold text-white mt-1">{data.metrics.winRate}</span>
                </div>
                <div className="glass-panel p-4 rounded-xl flex flex-col hover:-translate-y-0.5 transition-all">
                  <span className="text-[10px] uppercase font-bold text-red-500/80 tracking-wider">Max Drawdown</span>
                  <span className="text-2xl font-extrabold text-red-400 mt-1">{data.metrics.maxDrawdown}</span>
                </div>
                <div className="glass-panel p-4 rounded-xl flex flex-col hover:-translate-y-0.5 transition-all">
                  <span className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">Sharpe Ratio</span>
                  <span className="text-2xl font-extrabold text-indigo-300 mt-1">{data.metrics.sharpeRatio}</span>
                </div>
                <div className="glass-panel p-4 rounded-xl flex flex-col hover:-translate-y-0.5 transition-all">
                  <span className="text-[10px] uppercase font-bold text-amber-500/80 tracking-wider">Profit Factor</span>
                  <span className="text-2xl font-extrabold text-amber-400 mt-1">{data.metrics.profitFactor}</span>
                </div>
                <div className="glass-panel p-4 rounded-xl flex flex-col hover:-translate-y-0.5 transition-all">
                  <span className="text-[10px] uppercase font-bold text-teal-400 tracking-wider">Total Trades</span>
                  <span className="text-2xl font-extrabold text-teal-300 mt-1">{data.metrics.totalTrades}</span>
                </div>
                <div className="glass-panel p-4 rounded-xl flex flex-col hover:-translate-y-0.5 transition-all col-span-2 md:col-span-2">
                  <span className="text-[10px] uppercase font-bold text-gray-500 tracking-wider">Fees & Slippage Paid</span>
                  <span className="text-2xl font-extrabold text-gray-300 mt-1">{data.metrics.feesPaid}</span>
                </div>
              </div>
            )}

            {/* Main Content Area with tabs */}
            <div className="glass-panel rounded-2xl flex-1 flex flex-col overflow-hidden min-h-[500px]">
              {/* Tab headers */}
              <div className="flex border-b border-gray-800 bg-gray-900/40">
                <button
                  onClick={() => setActiveTab("chart")}
                  className={`flex-1 py-3 text-xs font-semibold border-b-2 transition-all ${
                    activeTab === "chart"
                      ? "border-emerald-500 text-emerald-400 bg-emerald-500/5"
                      : "border-transparent text-gray-400 hover:text-gray-200"
                  }`}
                >
                  📈 Equity Curve
                </button>
                <button
                  onClick={() => setActiveTab("spec")}
                  className={`flex-1 py-3 text-xs font-semibold border-b-2 transition-all ${
                    activeTab === "spec"
                      ? "border-emerald-500 text-emerald-400 bg-emerald-500/5"
                      : "border-transparent text-gray-400 hover:text-gray-200"
                  }`}
                >
                  ⚙️ Strategy Specification
                </button>
                <button
                  onClick={() => setActiveTab("signals")}
                  className={`flex-1 py-3 text-xs font-semibold border-b-2 transition-all ${
                    activeTab === "signals"
                      ? "border-emerald-500 text-emerald-400 bg-emerald-500/5"
                      : "border-transparent text-gray-400 hover:text-gray-200"
                  }`}
                >
                  🔔 Trade Signals
                </button>
              </div>

              {/* Tab Content */}
              <div className="p-6 flex-1 flex flex-col overflow-y-auto">
                {activeTab === "chart" && (
                  <div className="flex-1 min-h-[350px]">
                    {data ? (
                      <BacktestChart data={data.equity} />
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-500 italic">
                        Generate a strategy to visualize the backtest equity curve.
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "spec" && (
                  <div className="flex-1 flex flex-col gap-4">
                    {spec ? (
                      <div className="flex flex-col gap-4">
                        <div className="flex justify-between items-center border-b border-gray-800 pb-2">
                          <span className="text-sm font-semibold text-emerald-400">{spec.name}</span>
                          <span className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded font-bold font-mono">
                            TOKEN: {spec.token}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">Buy Entry Rules:</h4>
                            <ul className="flex flex-col gap-1.5">
                              {spec.buy_rules.map((rule, idx) => (
                                <li key={idx} className="bg-emerald-950/20 border border-emerald-900/50 p-2.5 rounded-lg text-xs text-gray-300">
                                  {rule.description || `${rule.indicator} ${rule.operator.replace(/_/g, ' ')} ${rule.value}`}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">Sell / Exit Rules:</h4>
                            <ul className="flex flex-col gap-1.5">
                              {spec.sell_rules.length > 0 ? (
                                spec.sell_rules.map((rule, idx) => (
                                  <li key={idx} className="bg-red-950/20 border border-red-900/50 p-2.5 rounded-lg text-xs text-gray-300">
                                    {rule.description || `${rule.indicator} ${rule.operator.replace(/_/g, ' ')} ${rule.value}`}
                                  </li>
                                ))
                              ) : (
                                <li className="text-xs text-gray-500 italic bg-gray-900/30 p-2.5 rounded-lg border border-gray-800">
                                  Default exits: Risk management TP/SL bounds.
                                </li>
                              )}
                            </ul>
                          </div>
                        </div>

                        <div className="border-t border-gray-800/80 pt-4">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">Risk Management:</h4>
                          <div className="grid grid-cols-3 gap-2 bg-gray-900/40 border border-gray-800 p-3 rounded-lg text-center">
                            <div>
                              <div className="text-[10px] text-gray-500 font-bold">TAKE PROFIT</div>
                              <div className="text-sm font-semibold text-emerald-400">+{spec.risk_management.take_profit_pct}%</div>
                            </div>
                            <div>
                              <div className="text-[10px] text-gray-500 font-bold">STOP LOSS</div>
                              <div className="text-sm font-semibold text-red-400">-{spec.risk_management.stop_loss_pct}%</div>
                            </div>
                            <div>
                              <div className="text-[10px] text-gray-500 font-bold">TRAILING STOP</div>
                              <div className="text-sm font-semibold text-gray-300">{spec.risk_management.trailing_stop_pct}%</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-500 italic">
                        Strategy specification not generated.
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "signals" && (
                  <div className="flex-1">
                    {data && data.signals.length > 0 ? (
                      <div className="overflow-x-auto max-h-[400px]">
                        <table className="w-full text-left">
                          <thead className="bg-gray-950/65 border-b border-gray-800 sticky top-0">
                            <tr>
                              <th className="p-3 text-[10px] uppercase font-bold text-gray-500">Timestamp</th>
                              <th className="p-3 text-[10px] uppercase font-bold text-gray-500">Action</th>
                              <th className="p-3 text-[10px] uppercase font-bold text-gray-500">Price</th>
                              <th className="p-3 text-[10px] uppercase font-bold text-gray-500">Reason / Metric Condition</th>
                            </tr>
                          </thead>
                          <tbody>
                            {data.signals.map((signal, idx) => (
                              <tr key={idx} className="border-b border-gray-800/40 hover:bg-gray-800/20 transition-colors">
                                <td className="p-3 text-xs text-gray-400">{new Date(signal.timestamp).toLocaleString()}</td>
                                <td className="p-3 text-xs">
                                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                    signal.type === 'BUY' 
                                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' 
                                      : 'bg-red-500/15 text-red-400 border border-red-500/20'
                                  }`}>
                                    {signal.type}
                                  </span>
                                </td>
                                <td className="p-3 text-xs font-mono font-semibold text-gray-300">
                                  ${signal.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                                </td>
                                <td className="p-3 text-xs text-gray-400">{signal.reason}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-500 italic">
                        No trade signals generated in the backtest.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
