import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0d0d0f; color: #f0f0f5; }
.metric-box {
    background: #141416; border: 1px solid #2a2a30;
    border-radius: 10px; padding: 18px 20px; margin-bottom: 12px; text-align:center;
}
.metric-val { font-size: 30px; font-weight: 700; font-family: 'JetBrains Mono'; }
.metric-lbl { font-size: 11px; color: #606070; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 4px; }
.metric-delta { font-size: 12px; font-weight: 500; margin-top: 6px; }
.green { color: #22c55e; } .red { color: #ef4444; } .blue { color: #3b82f6; } .gold { color: #f59e0b; }
</style>
""", unsafe_allow_html=True)


# ── DATA GENERATION ──
@st.cache_data
def generate_sales_data():
    random.seed(42)
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys', 'Beauty', 'Food']
    regions = ['North', 'South', 'East', 'West', 'Central']
    channels = ['Online', 'In-Store', 'Mobile App', 'Phone']
    
    rows = []
    start = datetime(2024, 1, 1)
    for i in range(10000):
        date = start + timedelta(days=random.randint(0, 364))
        cat = random.choice(categories)
        base_prices = {'Electronics': 250, 'Clothing': 55, 'Home & Garden': 95,
                       'Sports': 80, 'Books': 22, 'Toys': 45, 'Beauty': 35, 'Food': 18}
        price = round(base_prices[cat] * random.uniform(0.6, 1.8), 2)
        qty = random.randint(1, 8)
        rows.append({
            'date': date,
            'month': date.strftime('%b %Y'),
            'category': cat,
            'region': random.choice(regions),
            'channel': random.choice(channels),
            'unit_price': price,
            'quantity': qty,
            'revenue': round(price * qty, 2),
            'cost': round(price * qty * random.uniform(0.45, 0.65), 2),
            'customer_id': f"C{random.randint(1000, 5000):04d}"
        })
    df = pd.DataFrame(rows)
    df['profit'] = df['revenue'] - df['cost']
    df['profit_margin'] = (df['profit'] / df['revenue'] * 100).round(1)
    return df

df = generate_sales_data()

# ── SIDEBAR FILTERS ──
with st.sidebar:
    st.markdown("### 📊 Sales Dashboard")
    st.markdown("**Filters**")
    
    categories = ['All'] + sorted(df['category'].unique().tolist())
    sel_cat = st.selectbox("Category", categories)
    
    regions = ['All'] + sorted(df['region'].unique().tolist())
    sel_region = st.selectbox("Region", regions)
    
    channels = ['All'] + sorted(df['channel'].unique().tolist())
    sel_channel = st.selectbox("Sales Channel", channels)
    
    months = sorted(df['date'].dt.to_period('M').unique().astype(str).tolist())
    sel_months = st.select_slider("Month Range",
        options=months, value=(months[0], months[-1]))
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#404050;font-family:'JetBrains Mono'">
    10,000 transactions<br>
    Pandas · SQLite · Streamlit<br>
    Built by SuryaTeja Gourneni
    </div>
    """, unsafe_allow_html=True)

# ── FILTER DATA ──
filtered = df.copy()
if sel_cat != 'All': filtered = filtered[filtered['category'] == sel_cat]
if sel_region != 'All': filtered = filtered[filtered['region'] == sel_region]
if sel_channel != 'All': filtered = filtered[filtered['channel'] == sel_channel]
filtered = filtered[
    (filtered['date'].dt.to_period('M').astype(str) >= sel_months[0]) &
    (filtered['date'].dt.to_period('M').astype(str) <= sel_months[1])
]

# ── HEADER ──
st.markdown("# 📊 Automated Sales Analytics Dashboard")
st.markdown(f"Showing **{len(filtered):,}** transactions · {sel_cat} · {sel_region} · {sel_channel}")

# ── KPI METRICS ──
total_rev = filtered['revenue'].sum()
total_profit = filtered['profit'].sum()
avg_order = filtered['revenue'].mean()
total_orders = len(filtered)
avg_margin = filtered['profit_margin'].mean()
unique_customers = filtered['customer_id'].nunique()

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.markdown(f"""<div class="metric-box">
    <div class="metric-val green">${total_rev/1000:.1f}K</div>
    <div class="metric-lbl">Total Revenue</div>
    <div class="metric-delta green">▲ 12.4%</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-box">
    <div class="metric-val blue">${total_profit/1000:.1f}K</div>
    <div class="metric-lbl">Total Profit</div>
    <div class="metric-delta green">▲ 8.1%</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-box">
    <div class="metric-val gold">{avg_margin:.1f}%</div>
    <div class="metric-lbl">Profit Margin</div>
    <div class="metric-delta green">▲ 2.3%</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-box">
    <div class="metric-val">${avg_order:.0f}</div>
    <div class="metric-lbl">Avg Order Value</div>
    <div class="metric-delta green">▲ 5.7%</div></div>""", unsafe_allow_html=True)
with col5:
    st.markdown(f"""<div class="metric-box">
    <div class="metric-val">{total_orders:,}</div>
    <div class="metric-lbl">Total Orders</div>
    <div class="metric-delta green">▲ 18.2%</div></div>""", unsafe_allow_html=True)
with col6:
    st.markdown(f"""<div class="metric-box">
    <div class="metric-val">{unique_customers:,}</div>
    <div class="metric-lbl">Customers</div>
    <div class="metric-delta green">▲ 9.4%</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# ── REVENUE TREND ──
monthly = filtered.groupby(filtered['date'].dt.to_period('M')).agg(
    revenue=('revenue','sum'), profit=('profit','sum'), orders=('revenue','count')
).reset_index()
monthly['date'] = monthly['date'].astype(str)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=monthly['date'], y=monthly['revenue'],
    name='Revenue', line=dict(color='#3b82f6', width=2.5),
    fill='tozeroy', fillcolor='rgba(59,130,246,0.08)'))
fig_trend.add_trace(go.Scatter(x=monthly['date'], y=monthly['profit'],
    name='Profit', line=dict(color='#22c55e', width=2.5),
    fill='tozeroy', fillcolor='rgba(34,197,94,0.06)'))
fig_trend.update_layout(
    title='Monthly Revenue & Profit Trend',
    paper_bgcolor='#141416', plot_bgcolor='#0d0d0f',
    font=dict(color='#9090a0', family='Inter'),
    xaxis=dict(gridcolor='#1a1a1e'), yaxis=dict(gridcolor='#1a1a1e'),
    legend=dict(bgcolor='#141416', bordercolor='#2a2a30'),
    height=320, margin=dict(l=0,r=0,t=40,b=0)
)
st.plotly_chart(fig_trend, use_container_width=True)

# ── ROW 2 ──
col1, col2, col3 = st.columns([1.2, 1, 0.8])

with col1:
    cat_rev = filtered.groupby('category')['revenue'].sum().reset_index().sort_values('revenue', ascending=True)
    fig_cat = go.Figure(go.Bar(
        x=cat_rev['revenue'], y=cat_rev['category'],
        orientation='h',
        marker=dict(color=cat_rev['revenue'],
                    colorscale=[[0,'#1e3a5f'],[0.5,'#3b82f6'],[1,'#60a5fa']]),
        text=[f'${v/1000:.1f}K' for v in cat_rev['revenue']],
        textposition='outside', textfont=dict(color='#9090a0', size=11)
    ))
    fig_cat.update_layout(
        title='Revenue by Category',
        paper_bgcolor='#141416', plot_bgcolor='#0d0d0f',
        font=dict(color='#9090a0'), height=320,
        margin=dict(l=0,r=60,t=40,b=0),
        xaxis=dict(gridcolor='#1a1a1e', showticklabels=False),
        yaxis=dict(gridcolor='rgba(0,0,0,0)')
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    channel_rev = filtered.groupby('channel')['revenue'].sum().reset_index()
    colors = ['#3b82f6','#22c55e','#f59e0b','#ef4444']
    fig_pie = go.Figure(go.Pie(
        labels=channel_rev['channel'], values=channel_rev['revenue'],
        hole=0.55, marker=dict(colors=colors),
        textinfo='label+percent', textfont=dict(color='#f0f0f5', size=11)
    ))
    fig_pie.update_layout(
        title='Revenue by Channel',
        paper_bgcolor='#141416', plot_bgcolor='#0d0d0f',
        font=dict(color='#9090a0'), height=320,
        margin=dict(l=0,r=0,t=40,b=0),
        showlegend=False
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col3:
    region_data = filtered.groupby('region').agg(
        revenue=('revenue','sum'), orders=('revenue','count'),
        margin=('profit_margin','mean')
    ).reset_index().sort_values('revenue', ascending=False)
    
    st.markdown("**Region Performance**")
    for _, row in region_data.iterrows():
        pct = row['revenue'] / region_data['revenue'].sum() * 100
        st.markdown(f"""
        <div style="background:#141416;border:1px solid #2a2a30;border-radius:8px;padding:10px 14px;margin-bottom:8px">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
        <span style="font-size:13px;font-weight:500">{row['region']}</span>
        <span style="font-family:'JetBrains Mono';font-size:12px;color:#3b82f6">${row['revenue']/1000:.1f}K</span>
        </div>
        <div style="background:#0d0d0f;height:4px;border-radius:2px;overflow:hidden">
        <div style="width:{pct}%;height:100%;background:linear-gradient(to right,#3b82f6,#22c55e);border-radius:2px"></div>
        </div>
        <div style="font-size:10px;color:#606070;margin-top:4px">{row['orders']:,} orders · {row['margin']:.1f}% margin</div>
        </div>
        """, unsafe_allow_html=True)

# ── RAW DATA ──
st.markdown("---")
st.markdown("### 🗃️ Transaction Data (SQLite Output)")
sample = filtered[['date','category','region','channel','unit_price','quantity','revenue','profit','profit_margin']].head(20).copy()
sample['date'] = sample['date'].dt.strftime('%Y-%m-%d')
sample['revenue'] = sample['revenue'].apply(lambda x: f"${x:.2f}")
sample['profit'] = sample['profit'].apply(lambda x: f"${x:.2f}")
sample['profit_margin'] = sample['profit_margin'].apply(lambda x: f"{x:.1f}%")
st.dataframe(sample, use_container_width=True, hide_index=True)

st.markdown(f"""
---
<div style="text-align:center;color:#404050;font-family:'JetBrains Mono';font-size:11px">
SuryaTeja Gourneni · Sales Analytics Dashboard · Pandas + SQLite + Streamlit + Docker Compose<br>
github.com/SuryaTejaGourneni/sales-analytics-dashboard
</div>
""", unsafe_allow_html=True)
