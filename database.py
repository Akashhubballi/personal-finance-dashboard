import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

DB_FILE = "finance.db"

def get_connection(db_path: str = DB_FILE):
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_FILE):
    """Create database tables if they do not exist."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Categories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT CHECK(type IN ('Income', 'Expense')) NOT NULL
            );
        """)
        
        # Transactions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT CHECK(type IN ('Income', 'Expense')) NOT NULL,
                category TEXT NOT NULL,
                account TEXT NOT NULL DEFAULT 'Checking',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

def add_transaction(date: str, description: str, amount: float, t_type: str, category: str, account: str = "Checking", db_path: str = DB_FILE):
    """Insert a single transaction into the database."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, description, amount, type, category, account)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, description, abs(amount), t_type, category, account))
        conn.commit()

def fetch_transactions_df(db_path: str = DB_FILE) -> pd.DataFrame:
    """Read all transactions from SQL into a Pandas DataFrame."""
    with get_connection(db_path) as conn:
        query = "SELECT id, date, description, amount, type, category, account FROM transactions ORDER BY date DESC"
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df

def seed_sample_data(db_path: str = DB_FILE):
    """Seed the database with sample categories and realistic 90-day transactions."""
    init_db(db_path)
    
    categories = [
        ("Salary", "Income"),
        ("Freelance", "Income"),
        ("Investments", "Income"),
        ("Rent & Utilities", "Expense"),
        ("Groceries", "Expense"),
        ("Dining & Food", "Expense"),
        ("Transportation", "Expense"),
        ("Entertainment", "Expense"),
        ("Shopping", "Expense"),
        ("Healthcare", "Expense")
    ]
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Insert categories
        cursor.executemany("""
            INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)
        """, categories)
        
        # Check if transactions already exist
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        if count > 0:
            return  # Already seeded
        
        # Generate sample transactions across last 90 days
        sample_transactions = []
        today = datetime.today()
        
        # Bi-weekly salary
        for i in range(6):
            salary_date = (today - timedelta(days=i*14)).strftime("%Y-%m-%d")
            sample_transactions.append((salary_date, "Tech Corp Monthly Salary", 3500.0, "Income", "Salary", "Checking"))
            
        # Monthly rent
        for i in range(3):
            rent_date = (today - timedelta(days=i*30)).strftime("%Y-%m-%d")
            sample_transactions.append((rent_date, "Apartment Monthly Rent", 1400.0, "Expense", "Rent & Utilities", "Checking"))
            sample_transactions.append((rent_date, "Electric & Internet Bill", 150.0, "Expense", "Rent & Utilities", "Checking"))

        # Daily / Weekly expenses
        expense_options = [
            ("Whole Foods Market", 60, 140, "Expense", "Groceries", "Credit Card"),
            ("Trader Joe's", 35, 90, "Expense", "Groceries", "Credit Card"),
            ("Starbucks Coffee", 5, 12, "Expense", "Dining & Food", "Credit Card"),
            ("Chipotle Lunch", 12, 22, "Expense", "Dining & Food", "Credit Card"),
            ("Shell Gas Station", 40, 65, "Expense", "Transportation", "Credit Card"),
            ("Uber Ride", 15, 35, "Expense", "Transportation", "Credit Card"),
            ("Netflix Subscription", 15.99, 15.99, "Expense", "Entertainment", "Checking"),
            ("Cinema / Movies", 25, 45, "Expense", "Entertainment", "Credit Card"),
            ("Amazon Purchase", 20, 120, "Expense", "Shopping", "Credit Card"),
            ("Pharmacy / Meds", 15, 50, "Expense", "Healthcare", "Credit Card"),
            ("Upwork Freelance Client", 200, 600, "Income", "Freelance", "Checking"),
        ]

        for _ in range(60):
            days_ago = random.randint(1, 90)
            t_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            desc, min_amt, max_amt, t_type, cat, acc = random.choice(expense_options)
            amt = round(random.uniform(min_amt, max_amt), 2)
            sample_transactions.append((t_date, desc, amt, t_type, cat, acc))

        cursor.executemany("""
            INSERT INTO transactions (date, description, amount, type, category, account)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_transactions)
        conn.commit()

if __name__ == "__main__":
    print("Initializing and seeding database...")
    seed_sample_data()
    df = fetch_transactions_df()
    print(f"Database ready! Loaded {len(df)} transactions.")
    print("\nRecent 5 Transactions:")
    print(df.head(5))
