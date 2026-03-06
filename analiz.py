import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .login-box { max-width: 360px; margin: auto; padding: 25px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; }
    div[data-testid="stMetric"] { background-color: rgba(128, 128, 128, 0.08); border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 12px; }
    .plat-header { background: #f8f9fb; padding: 8px; border-radius: 8px; border-left: 5px solid #ff4b4b; margin: 15px 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ VE OTURUM SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026_final.csv'
USER_DB = 'kullanicilar.csv'
SESSION_FILE = 'active_session.txt'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Gun', 'Platform', 'Takipci', 'Etkilesim', 'YT_Izlenme'])
        df.to_csv(DB_FILE, index=False)
        return df
    df = pd.read_csv(DB_FILE)
    # HATA ÖNLEYİCİ: Eğer 'Gun' sütunu yoksa otomatik ekle
    if 'Gun' not in df.columns:
        df['Gun'] = 1
        df.to_csv(DB_FILE, index=False)
    return df

def kullanicilari_yukle():
    if not os.path.exists(USER_DB):
        df_u = pd.DataFrame([{"user": "admin", "pass": "teknostore123", "role": "Ana Kullanıcı"}])
        df_u.to_csv(USER_DB, index=False)
        return df_u
    return pd.read_csv(USER_DB)

# Oturum Durumu Başlatma
if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False

df_kullanicilar = kullanicilari_yukle()
KULLANICILAR = dict(zip(df_kullanicilar['user'], df_kullanicilar['pass']))

# --- 3. GİRİŞ EKRANI ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🔐 Yönetim Girişi</h3>", unsafe_allow_html=True)
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        if u in KULLANICILAR and KULLANICILAR[u] == p:
            st.session_state.oturum_durumu = True
            st.session_state.aktif_kullanici = u
            st.rerun()
        else: st.error("Hatalı giriş!")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 4. ANA PANEL ---
    df = veri_yukle()
    AYLAR_LISTESI = ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026", "Haziran 2026", 
                     "Temmuz 2026", "Ağustos 2026", "Eylül 2026", "Ekim 2026", "Kasım 2026", "Aralık 2026"]

    with st.sidebar:
        st.title("🚀 Menü")
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            marka_listesi = df['Marka'].unique().tolist() if not df.empty else ["Teknostore"]
            secilen_marka = st.selectbox("Marka Seçin:", marka_listesi)
            secilen_ay = st.selectbox("Ay Seçin:", AYLAR_LISTESI)

        st.divider()
        with st.expander("🛠️ Veri Girişi / Güncelle"):
            with st.form("veri_form"):
                f_m = st.selectbox("Marka", ["--- Yeni ---"] + df['Marka'].unique().tolist())
                f_yeni = st.text_input("Yeni Marka Adı")
                f_ay = st.selectbox("Ay", AYLAR_LISTESI)
                f_gun = st.number_input("Gün (1-31)", min_value=1, max_value=31, step=1)
                f_plat = st.selectbox("Platform", ["Instagram", "Facebook", "YouTube"])
                f_t = st.number_input("Takipçi", min_value=0)
                f_e = st.number_input("Etkileşim", min_value=0)
                f_y = st.number_input("YT İzlenme", min_value=0)
                
                if st.form_submit_button("Kaydet"):
                    m_ad = f_yeni if f_m == "--- Yeni ---" else f_m
                    if m_ad:
                        df = df[~((df['Marka'] == m_ad) & (df['Ay'] == f_ay) & (df['Gun'] == f_gun) & (df['Platform'] == f_plat))]
                        yeni_veri = {'Marka': m_ad, 'Ay': f_ay, 'Gun': f_gun, 'Platform': f_plat, 'Takipci': f_t, 'Etkilesim': f_e, 'YT_Izlenme': f_y}
                        df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.success("Veri Kaydedildi!")
                        st.rerun()

    # --- 5. GRAFİKLER ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Genel Marka Trendleri")
        if not df.empty:
            # Takipçi Çizgi Grafiği (Tüm Yıl)
            st.subheader("📈 Toplam Takipçi Gelişimi")
            fig_t = px.line(df.groupby(['Ay', 'Marka'])['Takipci'].sum().reset_index(), x='Ay', y='Takipci', color='Marka', markers=True)
            st.plotly_chart(fig_t, use_container_width=True)
            
            # Etkileşim Çizgi Grafiği
            st.subheader("🔥 Toplam Etkileşim Gelişimi")
            fig_e = px.line(df.groupby(['Ay', 'Marka'])['Etkilesim'].sum().reset_index(), x='Ay', y='Etkilesim', color='Marka', markers=True)
            st.plotly_chart(fig_e, use_container_width=True)

    else:
        # Marka Bazlı Günlük Detay
        m_ay_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)].sort_values(by='Gun')
        st.title(f"📊 {secilen_marka} - {secilen_ay} Analizi")

        for plat in ["Instagram", "Facebook", "YouTube"]:
            st.markdown(f'<div class="plat-header">{plat} Günlük Çizgi Grafikleri</div>', unsafe_allow_html=True)
            p_data = m_ay_df[m_ay_df['Platform'] == plat]
            if not p_data.empty:
                col1, col2 = st.columns(2)
                with col1:
                    # GÜNLÜK ÇİZGİ GRAFİĞİ
                    st.plotly_chart(px.line(p_data, x='Gun', y='Takipci', title=f"{plat} Takipçi Akışı", markers=True), use_container_width=True)
                with col2:
                    st.plotly_chart(px.line(p_data, x='Gun', y='Etkilesim', title=f"{plat} Etkileşim Akışı", markers=True, color_discrete_sequence=['#FFD43B']), use_container_width=True)

        st.divider()
        # Orijinal YouTube Bar Grafiği Korundu
        st.subheader("🎥 YouTube İzlenme Analizi")
        yt_data = m_ay_df[m_ay_df['Platform'] == 'YouTube']
        if not yt_data.empty:
            st.plotly_chart(px.bar(yt_data, x='Gun', y='YT_Izlenme', color='YT_Izlenme', color_continuous_scale='Reds'), use_container_width=True)
