import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# Tasarımını ve Metrik Kutularını Koruyan CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .login-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; margin-top: 20px; }
    .login-box { max-width: 360px; width: 100%; padding: 25px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; }
    div[data-testid="stMetric"] { background-color: rgba(128, 128, 128, 0.08); border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 12px; }
    .plat-header { background: #f8f9fb; padding: 8px; border-radius: 8px; border-left: 5px solid #ff4b4b; margin: 15px 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ VE KULLANICI SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026_final.csv'
USER_DB = 'kullanicilar.csv'
SESSION_FILE = 'active_session.txt'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Platform', 'Takipci', 'Etkilesim', 'YT_Izlenme'])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

def kullanicilari_yukle():
    if not os.path.exists(USER_DB):
        df_u = pd.DataFrame([{"user": "admin", "pass": "teknostore123", "role": "Ana Kullanıcı"}])
        df_u.to_csv(USER_DB, index=False)
        return df_u
    return pd.read_csv(USER_DB)

# --- 3. OTURUM KONTROLÜ (Hata Almamak İçin Tam Kısım) ---
df_kullanicilar = kullanicilari_yukle()
KULLANICILAR = dict(zip(df_kullanicilar['user'], df_kullanicilar['pass']))

if "oturum_durumu" not in st.session_state:
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            saved_user = f.read().strip()
            if saved_user in KULLANICILAR:
                st.session_state.oturum_durumu = True
                st.session_state.aktif_kullanici = saved_user
            else: st.session_state.oturum_durumu = False
    else: st.session_state.oturum_durumu = False

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    if os.path.exists("logo.png"): st.image("logo.png", width=250)
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0;'>🔐 Yönetim Girişi</h3>", unsafe_allow_html=True)
        u = st.text_input("Kullanıcı Adı", key="l_u")
        p = st.text_input("Şifre", type="password", key="l_p")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if u in KULLANICILAR and KULLANICILAR[u] == p:
                st.session_state.oturum_durumu = True
                st.session_state.aktif_kullanici = u
                with open(SESSION_FILE, 'w') as f: f.write(u)
                st.rerun()
            else: st.error("Hatalı giriş!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL ---
    df = veri_yukle()
    # Aralık ayına kadar tam liste
    AYLAR_LISTESI = ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026", "Haziran 2026", 
                     "Temmuz 2026", "Ağustos 2026", "Eylül 2026", "Ekim 2026", "Kasım 2026", "Aralık 2026"]

    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        st.info(f"👤: {st.session_state.aktif_kullanici}")

        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            markalar = df['Marka'].unique().tolist() if not df.empty else ["Veri Yok"]
            secilen_marka = st.selectbox("Marka Seçin:", markalar)
            secilen_ay = st.selectbox("Ay Seçin:", AYLAR_LISTESI) #
        
        st.divider()
        if st.button("Güvenli Çıkış", use_container_width=True):
            if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. RAPORLAMA VE GRAFİKLER ---
    if sayfa_modu == "📊 Marka Bazlı Detay":
        m_df = df[df['Marka'] == secilen_marka]
        m_ay_df = m_df[m_df['Ay'] == secilen_ay]
        
        st.title(f"📊 {secilen_marka} - {secilen_ay}")
        
        # Üst Metrikler
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_ay_df['Takipci'].sum()):,}")
        c2.metric("Toplam Etkileşim", f"{int(m_ay_df['Etkilesim'].sum()):,}")
        c3.metric("Seçilen Ay", secilen_ay)

        st.divider()

        # 🎯 İSTEĞİN: HER SOSYAL MEDYA İÇİN AYRI AYRI GRAFİKLER
        for plat in ["Instagram", "Facebook", "YouTube"]:
            st.markdown(f'<div class="plat-header">{plat} Detayları</div>', unsafe_allow_html=True)
            p_data = m_ay_df[m_ay_df['Platform'] == plat]
            col_a, col_b = st.columns(2)
            with col_a:
                st.plotly_chart(px.bar(p_data, x='Platform', y='Takipci', title=f"{plat} Takipçi", color_discrete_sequence=['#4B8BBE']), use_container_width=True)
            with col_b:
                st.plotly_chart(px.bar(p_data, x='Platform', y='Etkilesim', title=f"{plat} Etkileşim", color_discrete_sequence=['#FFD43B']), use_container_width=True)

        st.divider()

        # 🎯 İSTEĞİN: HEPSİNİN AYNI GRAFİKTE OLDUĞU KIYASLAMA
        st.subheader("⚖️ Genel Platform Kıyaslaması")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.plotly_chart(px.bar(m_ay_df, x='Platform', y='Takipci', color='Platform', title="Tüm Platformlar: Takipçi", barmode='group'), use_container_width=True)
        with col_c2:
            st.plotly_chart(px.bar(m_ay_df, x='Platform', y='Etkilesim', color='Platform', title="Tüm Platformlar: Etkileşim", barmode='group'), use_container_width=True)

        st.divider()

        # Orijinal Alt Grafikler
        col_alt1, col_alt2 = st.columns([2, 1])
        with col_alt1:
            st.subheader("🎥 YouTube İzlenme Analizi")
            yt_data = m_df[m_df['Platform'] == 'YouTube']
            if not yt_data.empty:
                st.plotly_chart(px.bar(yt_data, x='Ay', y='YT_Izlenme', color='YT_Izlenme', color_continuous_scale='Reds'), use_container_width=True)
        with col_alt2:
            st.subheader("🥧 Takipçi Dağılımı")
            st.plotly_chart(px.pie(m_ay_df, values='Takipci', names='Platform', hole=0.4), use_container_width=True)

    else:
        st.title("🏠 Genel Bakış")
        if not df.empty:
            st.plotly_chart(px.line(df.groupby(['Ay', 'Marka'])['Takipci'].sum().reset_index(), x='Ay', y='Takipci', color='Marka', markers=True), use_container_width=True)
