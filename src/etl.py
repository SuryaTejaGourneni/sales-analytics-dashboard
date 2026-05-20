import pandas as pd
from sqlalchemy import create_engine
from src.config import DB_URL, RAW_CSV_PATH, CURATED_TABLE, COLS

def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV_PATH)
    return df
def clean_transform(df: pd.DataFrame) -> pd.DataFrame:
    required = [
        COLS.order_id, COLS.order_date, COLS.customer_id, COLS.product, COLS.region, COLS.quantity, COLS.unit_price
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}. Update src/confog.py")
    
    df = df[required].copy()

    df[COLS.order_date] = pd.to_datetime(df[COLS.order_date], errors="coerce")
    df = df.dropna(subset=[COLS.order_date])

    df[COLS.quantity] = pd.to_numeric(df[COLS.unit_price], errors="coerce").fillna(0.0)

    df["revenue"] = df[COLS.quantity] * df[COLS.unit_price]

    df = df.drop_duplicates(subset=[COLS.order_id])

    return df

def load_to_postgres(df: pd.DataFrame) -> None:
    engine = create_engine(DB_URL)
    df.to_sql(CURATED_TABLE, engine, if_exists="replace", index=False)

def run():
    df = load_raw()
    curated = clean_transform(df)
    load_to_postgres(curated)
    print(f"Loaded {len(curated):,} rows into {CURATED_TABLE}")

if __name__ == "__main__":
    run()