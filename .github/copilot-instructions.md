# Copilot Instructions for Sales Analytics Dashboard

## Architecture Overview

**Three-tier architecture**: Data ingestion (ETL) → SQLite database → Streamlit UI
- `src/etl.py`: Raw CSV ingestion, cleaning, and loading to database
- `src/kpis.py`: Query layer for analytics computations and aggregations
- `app.py`: Streamlit frontend with filtering, metrics display, and data export

**Data flow**: CSV (`data/raw_sales.csv`) → cleaned/validated → SQLite (`analytics.db`) → query cache → UI metrics/charts

## Key Project Patterns

### Column Management via Dataclass
All sales data columns are defined in `src/config.py` as a frozen dataclass `COLS`:
```python
order_id, order_date, customer_id, product, region, quantity, unit_price
```
**Pattern**: Always reference columns via `COLS.<field>` (e.g., `COLS.order_id`), not hardcoded strings. This is enforced in `clean_transform()` validation.

### ETL Data Quality Enforcement
In `src/etl.py`, the `clean_transform()` function enforces:
- **Required columns validation**: Raises `ValueError` if any COLS field missing
- **Type coercion with fallback**: Dates use `errors="coerce"`, drops NaN; quantities use fillna(0.0)
- **Derived columns**: `revenue = quantity * unit_price` computed after type fixing
- **Deduplication**: `drop_duplicates(subset=[order_id])` removes duplicate orders

**Convention**: New ETL transformations should follow this coerce-then-validate pattern, not fail-fast.

### KPI Computation Safety
`compute_kpis()` handles edge cases:
- Checks `if total_orders` before division to avoid ZeroDivisionError in AOV calculation
- Returns floats/ints typed explicitly for JSON serialization to Streamlit
- Always returns a dict with consistent keys for UI metrics binding

### Streamlit Caching & Filtering
- `@st.cache_data` on `get_data()` caches DB reads; invalidates on script rerun only
- Filter logic in `app.py` creates copies (`f = df.copy()`) before subsetting to avoid SettingWithCopyWarning
- Region filter includes "All" option to reset filtering

## Critical Bugs / Known Issues

1. **`src/etl.py` line ~15**: `quantity` field assigned from `unit_price` column (copy-paste error)
   - Should be: `df[COLS.quantity] = pd.to_numeric(df[COLS.quantity], errors="coerce")`
   - Fix this if modifying revenue calculations

2. **Date parsing roundtrip**: SQLite stores dates as TEXT; `load_curated()` re-parses with `errors="coerce"` and drops NaNs to recover datetime type

## Database Configuration

- **Default (dev)**: SQLite at `analytics.db` via `DB_URL = "sqlite:///analytics.db"` in `config.py`
- **Docker optional**: `docker-compose.yml` provides PostgreSQL 16 (currently unused; environment config placeholder)
- **Table name**: `curated_sales` (hardcoded in `config` and `etl.py`)

To switch to Postgres: Update `DB_URL` in `config.py` and provide connection string (format: `postgresql://user:pass@host:port/db`)

## Dependencies & Runtime

**Stack**: Pandas (data), SQLAlchemy (ORM), Streamlit (UI), Plotly (charts)

**Running the app**:
1. Load data: `python -m src.etl` (creates/replaces `analytics.db`)
2. Start UI: `streamlit run app.py` (runs on `http://localhost:8501`)

**Development**:
- Venv expected at `.venv/`
- Use `requirements.txt` (pinned versions for reproducibility)

## Code Standards

- **Type hints**: Used sparingly (`-> pd.DataFrame`, `-> dict`) on public functions; not enforced in private helpers
- **Naming**: Shorthand for filtered DataFrame (`f` in `app.py`), KPI dict (`k`), report (`rep`) — follow this for consistency
- **String formatting**: f-strings used everywhere (not .format or %)
- **Error messages**: Include context; e.g., `f"Missing columns in CSV: {missing}."`

## Testing & Validation

No formal test suite yet. Manual validation points:
- ETL completeness: Print `f"Loaded {len(curated):,} rows"` after run
- UI metrics: Verify KPI values match manual calculation on small subset
- Date filtering: Check start/end date picker against rendered data

---

**Last updated**: After initial codebase review  
**Owner**: Data team  
