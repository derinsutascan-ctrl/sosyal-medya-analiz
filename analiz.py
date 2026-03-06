import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# CSS: Tasarımını Birebir Korur
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    div[data-testid="stMetric"] { background-color: rgba(128, 128, 128, 0.08); border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 12px; }
    .platform-header { background: #f0f2f6; padding: 10px; border-radius: 10px; margin: 20px 0; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ VE OTURUM SİSTEMİ (Önceki bölümlerle aynı) ---
DB_FILE = 'marka_veritabani_2026_final.csv'
USER_DB = 'kullanicilar.csv'
SESSION_FILE = 'active_session.txt'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Platform', 'Takipci', 'Etkilesim', 'YT_Izlenme'])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

# (Oturum kontrolü ve Giriş Ekranı kodları burada yer alır - Değişmediği için özet geçildi)
# ... [Oturum Kontrolü Kodları] ...

# --- 5. ANA PANEL ---
if "oturum_durumu" in st.session_state and st.session_state.oturum_durumu:
    df = veri_yukle()
    AYLAR_LISTESI = ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026", "Haziran 2026", 
                     "Temmuz 2026", "Ağustos 2026", "Eylül 2026", "Ekim 2026", "Kasım 2026", "Aralık 2026"]

    with st.sidebar:
        # (Sidebar menü ve veri ekleme formları aynı kaldı)
        st.title("🚀 Menü")
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        if sayfa_modu == "📊 Marka Bazlı Detay":
            secilen_marka = st.selectbox("Marka Seçin:", df['Marka'].unique() if not df.empty else ["Veri Yok"])
            secilen_ay = st.selectbox("Ay Seçin:", AYLAR_LISTESI)

    if sayfa_modu == "📊 Marka Bazlı Detay":
        m_df = df[df['Marka'] == secilen_marka]
        m_ay_df = m_df[m_df['Ay'] == secilen_ay]
        
        st.title(f"📊 {secilen_marka} Detaylı Analiz")
        
        # 1. BÖLÜM: PLATFORM BAZLI AYRI GRAFİKLER
        platforms = ["Instagram", "Facebook", "YouTube"]
        for plat in platforms:
            st.markdown(f'<div class="platform-header">{plat.upper()} PERFORMANSI</div>', unsafe_allow_html=True)
            p_data = m_ay_df[m_ay_df['Platform'] == plat]
            
            col1, col2 = st.columns(2)
            with col1:
                fig_t = px.bar(p_data, x='Platform', y='Takipci', title=f"{plat} Takipçi", color_discrete_sequence=['#4B8BBE'])
                st.plotly_chart(fig_t, use_container_width=True)
            with col2:
                fig_e = px.bar(p_data, x='Platform', y='Etkilesim', title=f"{plat} Etkileşim", color_discrete_sequence=['#FFD43B'])
                st.plotly_chart(fig_e, use_container_width=True)

        st.divider()

        # 2. BÖLÜM: TÜM PLATFORMLARIN AYNI GRAFİKTE OLDUĞU KIYASLAMA
        st.subheader("⚖️ Genel Platform Kıyaslaması (Aynı Grafikte)")
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            fig_comp_t = px.bar(m_ay_df, x='Platform', y='Takipci', color='Platform', barmode='group', title="Tüm Platformlar: Takipçi Kıyaslama")
            st.plotly_chart(fig_comp_t, use_container_width=True)
            
        with col_comp2:
            fig_comp_e = px.bar(m_ay_df, x='Platform', y='Etkilesim', color='Platform', barmode='group', title="Tüm Platformlar: Etkileşim Kıyaslama")
            st.plotly_chart(fig_comp_e, use_container_width=True)

        st.divider()

        # 3. BÖLÜM: ORİJİNAL YOUTUBE İZLENME VE TRENDLER
        col_bottom1, col_bottom2 = st.columns([2, 1])
        with col_bottom1:
            st.subheader("🎥 YouTube İzlenme Analizi")
            yt_data = m_df[m_df['Platform'] == 'YouTube']
            if not yt_data.empty:
                fig_yt = px.bar(yt_data, x='Ay', y='YT_Izlenme', color='YT_Izlenme', color_continuous_scale='Reds', title="Aylık YouTube İzlenme")
                st.plotly_chart(fig_yt, use_container_width=True)
        
        with col_bottom2:
            st.subheader("🥧 Takipçi Dağılımı")
            fig_pie = px.pie(m_ay_df, values='Takipci', names='Platform', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
