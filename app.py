import streamlit as st
import pandas as pd
from datetime import datetime, date

from database import init_db, seed_sample_data, fetch_transactions_df, add_transaction
import data_manager as dm
import charts

# Set Page Config
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize and seed database if not already done
init_db()
seed_sample_data()

# App Title & Header
st.title("💰 Personal Finance Dashboard")
st.caption("Powered by Python, SQLite, Pandas, Matplotlib & Streamlit")

# Fetch all data from SQLite
raw_df = fetch_transactions_df()

if raw_df.empty:
    st.warning("No transactions found in the database. Please add one from the sidebar!")
    st.stop()

# ----------------- SIDEBAR -----------------
st.sidebar.header("🔍 Filters & Controls")

# Date Filters
min_date = raw_df["date"].min().date()
max_date = raw_df["date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_d, end_d = selected_dates
elif isinstance(selected_dates, tuple) and len(selected_dates) == 1:
    start_d, end_d = selected_dates[0], selected_dates[0]
else:
    start_d, end_d = min_date, max_date

# Category Multiselect
all_categories = sorted(raw_df["category"].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Filter Categories",
    options=all_categories,
    default=all_categories
)

# Transaction Type Filter
t_type_filter = st.sidebar.radio(
    "Transaction Type",
    options=["All", "Income", "Expense"],
    horizontal=True
)

# Sidebar: Add New Transaction Form
st.sidebar.divider()
st.sidebar.subheader("➕ Add Transaction")

with st.sidebar.form("add_transaction_form", clear_on_submit=True):
    t_date = st.date_input("Date", value=date.today())
    t_desc = st.text_input("Description", placeholder="e.g. Grocery store")
    t_amt = st.number_input("Amount ($)", min_value=0.01, step=5.0, format="%.2f")
    t_type = st.selectbox("Type", ["Expense", "Income"])
    
    # Suggest common categories based on type
    cat_options = [
        "Groceries", "Dining & Food", "Rent & Utilities", 
        "Transportation", "Entertainment", "Shopping", 
        "Healthcare", "Salary", "Freelance", "Investments", "Other"
    ]
    t_cat = st.selectbox("Category", cat_options)
    t_acc = st.selectbox("Account", ["Checking", "Savings", "Credit Card", "Cash"])
    
    submitted = st.form_submit_button("Save Transaction")
    if submitted:
        if not t_desc.strip():
            st.sidebar.error("Please provide a description.")
        else:
            add_transaction(
                date=t_date.strftime("%Y-%m-%d"),
                description=t_desc,
                amount=float(t_amt),
                t_type=t_type,
                category=t_cat,
                account=t_acc
            )
            st.sidebar.success("Transaction added!")
            st.rerun()

# Apply Filters
filtered_df = dm.filter_transactions(
    raw_df,
    start_date=start_d,
    end_date=end_d,
    categories=selected_categories,
    t_type=t_type_filter
)

# ----------------- TOP METRIC KPIS -----------------
kpis = dm.get_kpis(filtered_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Income",
        value=f"${kpis['total_income']:,.2f}",
        delta=None
    )

with col2:
    st.metric(
        label="Total Expenses",
        value=f"${kpis['total_expense']:,.2f}",
        delta=None
    )

with col3:
    net_val = kpis['net_savings']
    st.metric(
        label="Net Savings",
        value=f"${net_val:,.2f}",
        delta=f"{'+' if net_val >= 0 else ''}${net_val:,.2f}",
        delta_color="normal" if net_val >= 0 else "inverse"
    )

with col4:
    st.metric(
        label="Savings Rate",
        value=f"{kpis['savings_rate']}%",
        help="Percentage of income retained after expenses"
    )

st.divider()

# ----------------- TABS -----------------
tab_analytics, tab_transactions, tab_categories = st.tabs([
    "📊 Financial Visualizations", 
    "📋 Transaction History", 
    "🏷️ Category Breakdown"
])

with tab_analytics:
    st.subheader("Monthly Cashflow Overview")
    monthly_df = dm.get_monthly_summary(filtered_df)
    
    fig_cashflow = charts.plot_monthly_cashflow(monthly_df)
    st.pyplot(fig_cashflow)
    
    col_donut, col_cum = st.columns(2)
    
    with col_donut:
        st.subheader("Expense Distribution")
        cat_df = dm.get_category_spending(filtered_df, t_type="Expense")
        if not cat_df.empty:
            fig_donut = charts.plot_category_donut(cat_df)
            st.pyplot(fig_donut)
        else:
            st.info("No expense data in the selected range.")
            
    with col_cum:
        st.subheader("Net Savings Growth")
        if not monthly_df.empty:
            fig_cum = charts.plot_cumulative_savings(monthly_df)
            st.pyplot(fig_cum)
        else:
            st.info("No monthly data available for savings trend.")

with tab_transactions:
    st.subheader(f"Transactions ({len(filtered_df)} records)")
    
    # Search box for transactions
    search_query = st.text_input("🔎 Search Description or Account", "")
    display_df = filtered_df.copy()
    
    if search_query:
        display_df = display_df[
            display_df["description"].str.contains(search_query, case=False, na=False) |
            display_df["account"].str.contains(search_query, case=False, na=False)
        ]
        
    # Format for clean display
    display_df["Formatted Date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    display_df["Formatted Amount"] = display_df.apply(
        lambda r: f"+${r['amount']:,.2f}" if r["type"] == "Income" else f"-${r['amount']:,.2f}", axis=1
    )
    
    view_cols = ["id", "Formatted Date", "description", "category", "Formatted Amount", "type", "account"]
    st.dataframe(
        display_df[view_cols].rename(columns={
            "id": "ID",
            "Formatted Date": "Date",
            "description": "Description",
            "category": "Category",
            "Formatted Amount": "Amount",
            "type": "Type",
            "account": "Account"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Export to CSV
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Filtered Transactions to CSV",
        data=csv_data,
        file_name="filtered_transactions.csv",
        mime="text/csv"
    )

with tab_categories:
    st.subheader("Spending Analysis by Category")
    cat_summary = dm.get_category_spending(filtered_df, t_type="Expense")
    
    if not cat_summary.empty:
        col_cat_tbl, col_cat_high = st.columns([1.5, 1])
        
        with col_cat_tbl:
            formatted_cat = cat_summary.copy()
            formatted_cat["Total ($)"] = formatted_cat["Total"].apply(lambda v: f"${v:,.2f}")
            formatted_cat["Share (%)"] = formatted_cat["Percentage"].apply(lambda v: f"{v}%")
            st.dataframe(
                formatted_cat[["Category", "Total ($)", "Share (%)"]],
                use_container_width=True,
                hide_index=True
            )
            
        with col_cat_high:
            top_cat = cat_summary.iloc[0]
            st.info(
                f"**Top Expense Category:** {top_cat['Category']}\n\n"
                f"**Total Spent:** ${top_cat['Total']:,.2f} ({top_cat['Percentage']}% of all expenses in selected period)"
            )
    else:
        st.info("No expenses found for category analysis.")
