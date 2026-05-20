import pandas as pd
from sqlalchemy import create_engine, text
from src.config import DB_URL, CURATED_TABLE, COLS

def load_curated() -> pd.DataFrame:
    engine = create_engine(DB_URL)
    df = pd.read_sql(text(f"SELECT * FROM {CURATED_TABLE}"), engine)
    # SQLite stores dates as strings — parse back to datetime
    df[COLS.order_date] = pd.to_datetime(df[COLS.order_date], errors="coerce")
    df = df.dropna(subset=[COLS.order_date])
    return df

def compute_kpis(df: pd.DataFrame) -> dict:
    total_revenue = float(df["revenue"].sum())
    total_orders = int(df[COLS.order_id].nunique())
    total_customers = int(df[COLS.customer_id].nunique())
    aov = (total_revenue / total_orders) if total_orders else 0.0
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "aov": aov,
    }

def weekly_report(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["week"] = df[COLS.order_date].dt.to_period("W").astype(str)
    return (
        df.groupby("week", as_index=False)
          .agg(revenue=("revenue", "sum"), orders=(COLS.order_id, "nunique"))
          .sort_values("week")
    )