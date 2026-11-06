import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set global matplotlib style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

def plot_monthly_cashflow(monthly_df: pd.DataFrame):
    """Generate a grouped bar chart showing Monthly Income vs Expense."""
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=100)
    
    if monthly_df.empty:
        ax.text(0.5, 0.5, "No monthly data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig
    
    months = monthly_df["Month"].tolist()
    x = np.arange(len(months))
    width = 0.35
    
    # Bars
    bars1 = ax.bar(x - width/2, monthly_df["Income"], width, label="Income", color="#2ecc71", alpha=0.88, edgecolor="none")
    bars2 = ax.bar(x + width/2, monthly_df["Expense"], width, label="Expense", color="#e74c3c", alpha=0.88, edgecolor="none")
    
    # Value annotations on top of bars
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f"${height:,.0f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8, color="#27ae60", weight="bold")
            
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f"${height:,.0f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8, color="#c0392b", weight="bold")
            
    ax.set_title("Monthly Income vs. Expense", fontsize=14, weight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=10)
    ax.set_ylabel("Amount ($)", fontsize=11)
    ax.legend(frameon=True, facecolor="white", edgecolor="#e0e0e0")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    # Clean top and right borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    fig.tight_layout()
    return fig

def plot_category_donut(category_df: pd.DataFrame, title: str = "Expense Distribution by Category"):
    """Generate a clean donut chart for spending by category."""
    fig, ax = plt.subplots(figsize=(7, 5), dpi=100)
    
    if category_df.empty:
        ax.text(0.5, 0.5, "No category data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig
    
    # If more than 6 categories, group the smaller ones into 'Other'
    plot_df = category_df.copy()
    if len(plot_df) > 6:
        top_5 = plot_df.iloc[:5]
        other_sum = plot_df.iloc[5:]["Total"].sum()
        other_row = pd.DataFrame([{"Category": "Other", "Total": other_sum, "Percentage": round(other_sum / plot_df["Total"].sum() * 100, 1)}])
        plot_df = pd.concat([top_5, other_row], ignore_index=True)
        
    palette = ["#3498db", "#9b59b6", "#e67e22", "#1abc9c", "#f39c12", "#95a5a6", "#34495e"]
    colors = palette[:len(plot_df)]
    
    wedges, texts, autotexts = ax.pie(
        plot_df["Total"],
        labels=plot_df["Category"],
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.78,
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_weight("bold")
        autotext.set_fontsize(9)
        
    for text in texts:
        text.set_fontsize(9.5)
        
    ax.set_title(title, fontsize=13, weight="bold", pad=15)
    fig.tight_layout()
    return fig

def plot_cumulative_savings(monthly_df: pd.DataFrame):
    """Generate an area chart tracking cumulative net savings."""
    fig, ax = plt.subplots(figsize=(9, 4), dpi=100)
    
    if monthly_df.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig
        
    df_copy = monthly_df.copy()
    df_copy["Cumulative"] = df_copy["Net Savings"].cumsum()
    
    x = df_copy["Month"]
    y = df_copy["Cumulative"]
    
    ax.plot(x, y, marker="o", linewidth=2.5, color="#2980b9", label="Cumulative Savings ($)")
    ax.fill_between(x, y, color="#3498db", alpha=0.18)
    
    for i, txt in enumerate(y):
        ax.annotate(f"${txt:,.0f}", (x.iloc[i], y.iloc[i]),
                    textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=9, weight="bold", color="#1f618d")
        
    ax.set_title("Cumulative Savings Growth Over Time", fontsize=13, weight="bold", pad=12)
    ax.set_ylabel("Total Saved ($)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    fig.tight_layout()
    return fig
