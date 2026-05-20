import streamlit as st
import plotly.express as px
from src.kpis import load_curated, compute_kpis, weekly_report
from src.config import COLS

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")

@st.cache_data
def get_data():
    return load_curated()

df = get_data()

st.title("Automated Sales Analytics Dashboard")

# Filters
min_date = df[COLS.order_date].min()
max_date = df[COLS.order_date].max()

col1, col2, col3 = st.columns(3)
with col1:
    start = st.date_input("Start date", value=min_date.date())
with col2:
    end = st.date_input("End date", value=max_date.date())
with col3:
    region = st.selectbox("Region", ["All"] + sorted(df[COLS.region].dropna().unique().tolist()))

f = df[(df[COLS.order_date].dt.date >= start) & (df[COLS.order_date].dt.date <= end)].copy()
if region != "All":
    f = f[f[COLS.region] == region]

k = compute_kpis(f)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Revenue", f"${k['total_revenue']:,.2f}")
m2.metric("Orders", f"{k['total_orders']:,}")
m3.metric("Customers", f"{k['total_customers']:,}")
m4.metric("Avg Order Value", f"${k['aov']:,.2f}")

st.subheader("Revenue by Week")
rep = weekly_report(f)
fig = px.line(rep, x="week", y="revenue", markers=True)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Top Products")
top = (f.groupby(COLS.product, as_index=False)["revenue"].sum().sort_values("revenue", ascending=False).head(10))
fig2 = px.bar(top, x=COLS.product, y="revenue")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Export Weekly Report")
csv = rep.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", data=csv, file_name="weekly_report.csv", mime="text/csv")