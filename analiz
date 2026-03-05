import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Marka Analiz Paneli", layout="wide")

# Arka planı beyaz yapmak ve kartları güzelleştirmek için CSS
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- YAN MENÜ (SIDEBAR) ---
st.sidebar.title("🏢 Marka Seçimi")
marka = st.sidebar.selectbox("Lütfen bir marka seçin:", ["Teknostore", "Aula", "Nowgo"])

# --- VERİLER (Markalara Özel) ---
data_map = {
    "Teknostore": {"renk": "#007bff", "takipci": 15400, "erisim": 42000, "ig": 450, "fb": 200, "yt": 350},
    "Aula": {"renk": "#6f42c1", "takipci": 8200, "erisim": 18500, "ig": 600, "fb": 150, "yt": 100},
    "Nowgo": {"renk": "#28a745", "takipci": 19800, "erisim": 76000, "ig": 300, "fb": 400, "yt": 500}
}
m = data_map[marka]

# --- ÜST PANEL: ÖZET KARTLARI ---
st.title(f"📊 {marka} Sosyal Medya Raporu")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Toplam Takipçi", f"{m['takipci']:,}", "+5%")
col2.metric("Aylık Erişim", f"{m['erisim']:,}", "+12%")
col3.metric("Etkileşim Oranı", "%4.8", "0.3%")
col4.metric("Aktif Reklam", "4 Adet", "Sabit")

st.divider()

# --- ORTA PANEL: GRAFİKLER ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Platform Bazlı Etkileşim")
    df_plot = pd.DataFrame({
        'Platform': ['Instagram', 'Facebook', 'YouTube'],
        'Etkileşim': [m['ig'], m['fb'], m['yt']]
    })
    fig = px.bar(df_plot, x='Platform', y='Etkileşim', color='Platform',
                 color_discrete_sequence=[m['renk']], template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Kanal Dağılımı (%)")
    fig_pie = px.pie(df_plot, values='Etkileşim', names='Platform', hole=0.4, template="plotly_white")
    st.plotly_chart(fig_pie, use_container_width=True)

# --- ALT PANEL: HEDEFLER VE NOTLAR ---
st.divider()
k1, k2 = st.columns(2)

with k1:
    st.subheader("🎯 Aylık Hedef İlerlemesi")
    st.write("Takipçi Hedefi (25.000)")
    st.progress(m['takipci'] / 25000)
    st.write("Erişim Hedefi (100.000)")
    st.progress(m['erisim'] / 100000)

with k2:
    st.subheader("📝 Strateji Notları")
    st.info(f"{marka} için bu hafta video içerik üretimi artırılmalı ve yorumlara dönüş hızı optimize edilmeli.")
