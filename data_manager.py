import pandas as pd
from typing import Dict, Any, Tuple

def get_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate core financial health indicators from the transactions DataFrame."""
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expense": 0.0,
            "net_savings": 0.0,
            "savings_rate": 0.0,
            "transaction_count": 0
        }
    
    income = df[df["type"] == "Income"]["amount"].sum()
    expense = df[df["type"] == "Expense"]["amount"].sum()
    net = income - expense
    savings_rate = (net / income * 100) if income > 0 else 0.0
    
    return {
        "total_income": round(income, 2),
        "total_expense": round(expense, 2),
        "net_savings": round(net, 2),
        "savings_rate": round(savings_rate, 1),
        "transaction_count": len(df)
    }

def get_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Group transactions by Month and Type to produce a monthly cashflow summary."""
    if df.empty:
        return pd.DataFrame(columns=["Month", "Income", "Expense", "Net Savings"])
    
    df_copy = df.copy()
    df_copy["Month"] = df_copy["date"].dt.to_period("M").astype(str)
    
    pivot = df_copy.pivot_table(
        index="Month",
        columns="type",
        values="amount",
        aggfunc="sum",
        fill_value=0.0
    ).reset_index()
    
    for col in ["Income", "Expense"]:
        if col not in pivot.columns:
            pivot[col] = 0.0
            
    pivot["Net Savings"] = pivot["Income"] - pivot["Expense"]
    pivot = pivot.sort_values(by="Month")
    return pivot

def get_category_spending(df: pd.DataFrame, t_type: str = "Expense") -> pd.DataFrame:
    """Aggregate spending or earnings grouped by category with percentage share."""
    filtered = df[df["type"] == t_type]
    if filtered.empty:
        return pd.DataFrame(columns=["Category", "Total", "Percentage"])
    
    cat_summary = filtered.groupby("category")["amount"].sum().reset_index()
    cat_summary.columns = ["Category", "Total"]
    total_val = cat_summary["Total"].sum()
    cat_summary["Percentage"] = (cat_summary["Total"] / total_val * 100).round(1)
    cat_summary = cat_summary.sort_values(by="Total", ascending=False)
    return cat_summary

def filter_transactions(
    df: pd.DataFrame,
    start_date: Any = None,
    end_date: Any = None,
    categories: list = None,
    t_type: str = "All"
) -> pd.DataFrame:
    """Apply interactive filters on the DataFrame."""
    if df.empty:
        return df
    
    filtered = df.copy()
    
    if start_date:
        filtered = filtered[filtered["date"].dt.date >= start_date]
    if end_date:
        filtered = filtered[filtered["date"].dt.date <= end_date]
    if categories:
        filtered = filtered[filtered["category"].isin(categories)]
    if t_type and t_type != "All":
        filtered = filtered[filtered["type"] == t_type]
        
    return filtered
