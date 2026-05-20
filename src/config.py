from dataclasses import dataclass

@dataclass(frozen=True)
class SalesColumns:
    order_id: str = "order_id"
    order_date: str = "order_date"
    customer_id: str = "customer_id"
    product: str = "product"
    region: str = "region"
    quantity: str = "quantity"
    unit_price: str = "unit_price"

COLS = SalesColumns()

DB_URL = "sqlite:///analytics.db"
RAW_CSV_PATH = "data/raw_sales.csv"
CURATED_TABLE = "curated_sales"