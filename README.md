# 💰 Personal Finance Dashboard

An interactive personal finance analytics dashboard built with **Python**, **SQL (SQLite)**, **Pandas**, **Matplotlib (`pyplot`)**, and **Streamlit**.

---

## 🛠️ Tech Stack & Skills Breakdown

| Technology | Role in Project | File |
| :--- | :--- | :--- |
| **SQL (SQLite)** | Database schema, transactions table, CRUD storage & persistence | `database.py` |
| **Pandas** | In-memory data aggregation, pivot tables, filtering, KPIs, and monthly rollups | `data_manager.py` |
| **Matplotlib (`pyplot`)** | Custom data visualizations (grouped cashflow bars, category donut chart, savings trend) | `charts.py` |
| **Streamlit** | Interactive UI, sidebar filters, transaction forms, metric cards, and CSV export | `app.py` |
| **Python** | Core logic, modular architecture, and orchestration | All files |

---

## 📁 Project Structure

```
personal-finance-dashboard/
├── database.py       # SQL schema definition, seed data, and query functions
├── data_manager.py   # Pandas calculations, monthly summaries, KPIs & filters
├── charts.py         # Matplotlib/pyplot figure generators
├── app.py            # Streamlit dashboard interface & user controls
├── requirements.txt  # Project dependencies
└── README.md         # Documentation and setup instructions
```

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Dashboard
```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## ✨ Features
- **Key Metrics (KPIs):** Real-time Total Income, Total Expenses, Net Savings, and Savings Rate.
- **Dynamic Cashflow Charts:** Monthly income vs. expense comparison via Matplotlib.
- **Spending Distribution:** Visual donut chart breaking down expenses by category.
- **Savings Growth:** Cumulative net savings line chart over time.
- **Interactive Filters:** Filter by date range, transaction type, or specific categories.
- **Add Transactions on the Fly:** Sidebar form to immediately log new expenses or income into SQLite.
- **Data Export:** Download filtered transactions into a `.csv` file.
