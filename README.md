# Quick Commerce Supply Chain Analytics
### Live Inventory Stockout Simulator & Control Tower | Safety Stock · ROP · Streamlit

---

## What Business Problem Does This Solve?

Quick commerce (10–30 minute delivery) lives or dies on one thing:
**having the right product in stock at the right time.**

A stockout means a lost order, a failed delivery promise, and a churned customer.
Overstock means cash locked in inventory that isn't moving.

**This project answers 3 questions every supply chain and operations team faces:**
1. How much safety stock do we need to never run out — without overstocking?
2. At what inventory level should we trigger a reorder? (Reorder Point)
3. What happens to stockout risk if demand spikes or lead time increases?

---

## Business Results

| Metric | Value |
|---|---|
| Method | Operations Research — Safety Stock + ROP formulas |
| Simulation | Live what-if scenario testing (adjust demand, lead time, service level) |
| Output | Optimal safety stock level + reorder point per SKU |
| Business impact | Reduce stockouts without increasing inventory holding costs |

---

## Key Business Insights This Tool Provides

- **Safety Stock formula** accounts for demand variability AND lead time variability — not just average demand
- **Reorder Point (ROP)** tells warehouse managers exactly when to place the next order
- **Stockout simulator** lets operations teams test "what if demand doubles during a festival week?"
- **Service level toggle** — set 95% or 99% service level and see how inventory requirement changes
- **Control tower view** — live dashboard showing which SKUs are at risk right now

---

## Live Demo

🌐 **[Live Streamlit App](https://quick-commerce-supply-chain-analytics-jsmnrfcwueq6d2l4hpbnnt.streamlit.app/)**

Adjust demand variability, lead time, and service level sliders — see safety stock and ROP update in real time.

---

## How It Works

```
Input Parameters (via UI sliders)
    │  Avg Daily Demand · Demand Std Dev
    │  Avg Lead Time · Lead Time Std Dev
    │  Target Service Level (95% / 99%)
    ▼
Operations Research Engine
    │
    ├── Safety Stock = Z × √(Lead Time × σ_demand² + Avg Demand² × σ_lead²)
    └── Reorder Point = (Avg Demand × Avg Lead Time) + Safety Stock
    ▼
Streamlit Dashboard
    ├── Optimal Safety Stock quantity
    ├── Reorder Point trigger level
    ├── Stockout probability curve
    └── Inventory cost vs service level trade-off chart
```

---

## Operations Research Concepts Used

| Concept | Purpose |
|---|---|
| Safety Stock | Buffer inventory against demand & supply uncertainty |
| Reorder Point (ROP) | Trigger level to place a new purchase order |
| Service Level (Z-score) | Probability of not running out of stock |
| EOQ (Economic Order Quantity) | Optimal order size to minimise total inventory cost |
| Stockout Simulation | What-if scenario modelling for demand spikes |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Analytics engine | Python, Pandas, NumPy, SciPy |
| Operations Research | Safety Stock formula, ROP, EOQ |
| Web app | Streamlit |
| Visualisation | Plotly / Matplotlib |

---

## How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/premchavan772005-spec/quick-commerce-supply-chain-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

---

*Built by Prem Chavan | Data Analyst*
*Skills: Python · Pandas · Operations Research · Supply Chain Analytics · Streamlit*
