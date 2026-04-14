import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Maven Roasters Performance",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# PALETTE & CSS GLOBAL
# ==========================================
# Color palette: Deep espresso dark bg, warm cream text, gold accents
COLORS = {
    'bg':         '#0F0A07',
    'surface':    '#1A1208',
    'card':       '#221A0F',
    'border':     '#3D2E1A',
    'gold':       '#C8922A',
    'gold_light': '#E8B84B',
    'cream':      '#F2E4C8',
    'muted':      '#8C7A5E',
    'loc1':       '#C8922A',   # gold
    'loc2':       '#7EC8A0',   # sage green
    'loc3':       '#C87A5E',   # terracotta
}

PLOT_COLORS = [COLORS['loc1'], COLORS['loc2'], COLORS['loc3']]
SEQUENTIAL   = ['#2D1A05', '#5C3A10', '#8C5C1A', '#C8922A', '#E8B84B', '#F2D98C']

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {COLORS['bg']};
    color: {COLORS['cream']};
}}

/* Remove Streamlit default padding */
.block-container {{
    padding: 2rem 3rem 4rem 3rem !important;
    max-width: 1400px;
}}

/* Hide default header */
header[data-testid="stHeader"] {{
    background-color: {COLORS['bg']};
}}

/* ---- Hero header ---- */
.hero-wrap {{
    display: flex;
    align-items: center;
    gap: 24px;
    margin-bottom: 8px;
}}
.hero-badge {{
    font-size: 3.5rem;
    line-height: 1;
}}
.hero-title {{
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: {COLORS['cream']};
    letter-spacing: -0.5px;
    margin: 0;
    line-height: 1.1;
}}
.hero-subtitle {{
    font-size: 0.95rem;
    color: {COLORS['muted']};
    margin: 4px 0 0 0;
    letter-spacing: 0.3px;
}}
.gold-bar {{
    height: 3px;
    background: linear-gradient(90deg, {COLORS['gold']}, {COLORS['gold_light']}, transparent);
    border: none;
    margin: 16px 0 28px 0;
    border-radius: 2px;
}}

/* ---- KPI Cards ---- */
.kpi-row {{
    display: flex;
    gap: 20px;
    margin-bottom: 36px;
}}
.kpi-card {{
    flex: 1;
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {COLORS['gold']}, {COLORS['gold_light']});
}}
.kpi-label {{
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: {COLORS['muted']};
    margin-bottom: 10px;
}}
.kpi-value {{
    font-family: 'Playfair Display', serif;
    font-size: 2.1rem;
    font-weight: 600;
    color: {COLORS['gold_light']};
    line-height: 1;
    margin-bottom: 8px;
}}
.kpi-desc {{
    font-size: 0.75rem;
    color: {COLORS['muted']};
}}

/* ---- Section headers ---- */
.section-header {{
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: {COLORS['cream']};
    margin: 0 0 4px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.section-sub {{
    font-size: 0.8rem;
    color: {COLORS['muted']};
    margin-bottom: 16px;
    letter-spacing: 0.2px;
}}
.section-divider {{
    height: 1px;
    background: {COLORS['border']};
    margin: 32px 0 24px 0;
    border: none;
}}

/* ---- Chart wrapper ---- */
.chart-card {{
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 4px;
}}

/* Override Streamlit metric */
div[data-testid="metric-container"] {{
    display: none;
}}

/* Footer */
.footer {{
    text-align: center;
    margin-top: 48px;
    font-size: 0.75rem;
    color: {COLORS['muted']};
    letter-spacing: 0.5px;
    padding: 20px 0;
    border-top: 1px solid {COLORS['border']};
}}
.footer span {{
    color: {COLORS['gold']};
}}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. FUNGSI MEMUAT & MEMBERSIHKAN DATA
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_excel('Coffee Shop Sales.xlsx')

    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['hour'] = pd.to_datetime(df['transaction_time'], format='%H:%M:%S').dt.hour
    df['revenue'] = df['transaction_qty'] * df['unit_price']

    hari_indo   = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    hari_inggris = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    map_hari = dict(zip(hari_inggris, hari_indo))

    df['day_name'] = df['transaction_date'].dt.day_name().map(map_hari)
    df['day_name'] = pd.Categorical(df['day_name'], categories=hari_indo, ordered=True)

    def categorize_time(h):
        if 6 <= h < 11:  return 'Pagi (06-11)'
        elif 11 <= h < 15: return 'Siang (11-15)'
        elif 15 <= h < 18: return 'Sore (15-18)'
        else:              return 'Malam (18+)'

    df['time_of_day'] = df['hour'].apply(categorize_time)
    df['time_of_day'] = pd.Categorical(
        df['time_of_day'],
        categories=['Pagi (06-11)', 'Siang (11-15)', 'Sore (15-18)', 'Malam (18+)'],
        ordered=True
    )
    return df

df = load_data()


# ==========================================
# PLOTLY TEMPLATE (dark, consistent)
# ==========================================
PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color=COLORS['cream'], size=12),
    title_font=dict(family='Playfair Display', color=COLORS['cream'], size=15),
    legend=dict(
        bgcolor='rgba(0,0,0,0)',
        bordercolor=COLORS['border'],
        borderwidth=1,
        font=dict(color=COLORS['muted'], size=11),
    ),
    xaxis=dict(
        gridcolor=COLORS['border'],
        linecolor=COLORS['border'],
        tickcolor=COLORS['muted'],
        tickfont=dict(color=COLORS['muted']),
        title_font=dict(color=COLORS['muted']),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor=COLORS['border'],
        linecolor=COLORS['border'],
        tickcolor=COLORS['muted'],
        tickfont=dict(color=COLORS['muted']),
        title_font=dict(color=COLORS['muted']),
        zeroline=False,
    ),
    margin=dict(t=30, b=10, l=10, r=10),
    hovermode='x unified',
)


# ==========================================
# 3. HERO HEADER
# ==========================================
st.markdown("""
<div class="hero-wrap">
  <div class="hero-badge">☕</div>
  <div>
    <p class="hero-title">Maven Roasters</p>
    <p class="hero-subtitle">Executive Performance Dashboard · Sales Analytics</p>
  </div>
</div>
<div class="gold-bar"></div>
""", unsafe_allow_html=True)


# ==========================================
# 4. KPI SCORECARDS
# ==========================================
total_revenue    = df['revenue'].sum()
total_transactions = df['transaction_id'].nunique()
aov              = total_revenue / total_transactions

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">Total Revenue</div>
    <div class="kpi-value">${total_revenue:,.0f}</div>
    <div class="kpi-desc">Pendapatan kotor keseluruhan</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Transactions</div>
    <div class="kpi-value">{total_transactions:,}</div>
    <div class="kpi-desc">Jumlah pesanan tercatat</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg. Order Value</div>
    <div class="kpi-value">${aov:.2f}</div>
    <div class="kpi-desc">Rata-rata pendapatan per nota</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. GRAFIK 1: TREN PENJUALAN HARIAN
# ==========================================
st.markdown('<p class="section-header">Tren Pendapatan Harian</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Revenue harian dipisah berdasarkan lokasi toko</p>', unsafe_allow_html=True)

trend_df = df.groupby(['transaction_date', 'store_location'])['revenue'].sum().reset_index()

fig_trend = px.line(
    trend_df, x='transaction_date', y='revenue', color='store_location',
    color_discrete_sequence=PLOT_COLORS,
)
fig_trend.update_traces(line=dict(width=2), opacity=0.9)
fig_trend.update_layout(
    **PLOT_LAYOUT,
    title="Tren Pendapatan Harian per Lokasi Toko",
    xaxis_title="Tanggal",
    yaxis_title="Pendapatan ($)",
    legend_title="Lokasi Toko",
    # hovermode="x unified",
    height=340,
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# ==========================================
# 6. GRAFIK 2 & 3: POLA KERAMAIAN
# ==========================================
st.markdown('<p class="section-header">Analisis Pola Keramaian</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Hari & jam sibuk berdasarkan volume dan nilai transaksi</p>', unsafe_allow_html=True)

col4, col5 = st.columns(2, gap="large")

with col4:
    aov_day_time = df.groupby(['day_name', 'time_of_day'])['revenue'].mean().reset_index()

    fig_day = px.bar(
        aov_day_time, x='day_name', y='revenue', color='time_of_day',
        color_discrete_sequence=SEQUENTIAL[1:],
        barmode='stack',
    )
    fig_day.update_layout(
        **PLOT_LAYOUT,
        title="Rata-rata Nilai Transaksi — Hari & Waktu",
        xaxis_title="Hari",
        yaxis_title="Rata-rata Transaksi ($)",
        legend_title="Waktu",
        height=360,
    )
    st.plotly_chart(fig_day, use_container_width=True)

with col5:
    hour_loc = df.groupby(['hour', 'store_location'])['transaction_id'].count().reset_index()

    fig_hour = px.line(
        hour_loc, x='hour', y='transaction_id', color='store_location',
        color_discrete_sequence=PLOT_COLORS,
        markers=True,
    )
    fig_hour.update_traces(line=dict(width=2.5), marker=dict(size=6))
    fig_hour.update_layout(
    **PLOT_LAYOUT,
    title="Volume Transaksi — Jam & Lokasi",
    yaxis_title="Total Transaksi",
    legend_title="Lokasi Toko",
    height=360,
    )
    fig_hour.update_xaxes(
        title_text="Jam (06:00 – 20:00)",
        tickmode='linear', tick0=6, dtick=1,
    )
    st.plotly_chart(fig_hour, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# ==========================================
# 7. GRAFIK 4A & 4B: PERFORMA PRODUK
# ==========================================
st.markdown('<p class="section-header">Performa Produk</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Produk paling laris vs paling menghasilkan pendapatan</p>', unsafe_allow_html=True)

col6, col7 = st.columns(2, gap="large")

top_qty = (df.groupby('product_type')['transaction_qty'].sum()
             .reset_index().nlargest(10, 'transaction_qty')
             .sort_values('transaction_qty', ascending=True))
top_rev = (df.groupby('product_type')['revenue'].sum()
             .reset_index().nlargest(10, 'revenue')
             .sort_values('revenue', ascending=True))

with col6:
    fig_qty = px.bar(
        top_qty, x='transaction_qty', y='product_type', orientation='h',
        color_discrete_sequence=[COLORS['loc2']],
        text_auto='.2s',
    )
    fig_qty.update_traces(
        textfont=dict(color=COLORS['cream'], size=10),
        marker_line_width=0,
        opacity=0.9,
    )
    fig_qty.update_layout(
        **PLOT_LAYOUT,
        title="Top 10 Produk — Kuantitas Terjual",
        xaxis_title="Total Cup / Pcs Terjual",
        yaxis_title="",
        height=400,
    )
    st.plotly_chart(fig_qty, use_container_width=True)

with col7:
    fig_rev = px.bar(
        top_rev, x='revenue', y='product_type', orientation='h',
        color_discrete_sequence=[COLORS['gold']],
        text_auto='$.2s',
    )
    fig_rev.update_traces(
        textfont=dict(color=COLORS['cream'], size=10),
        marker_line_width=0,
        opacity=0.9,
    )
    fig_rev.update_layout(
        **PLOT_LAYOUT,
        title="Top 10 Produk — Total Pendapatan",
        xaxis_title="Total Pendapatan ($)",
        yaxis_title="",
        height=400,
    )
    st.plotly_chart(fig_rev, use_container_width=True)


# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer">
  Crafted with <span>♥</span> using Streamlit &amp; Plotly &nbsp;·&nbsp; Maven Roasters Analytics Suite
</div>
""", unsafe_allow_html=True)
