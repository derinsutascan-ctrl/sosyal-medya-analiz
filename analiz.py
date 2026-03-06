import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(
    page_title="Teknostore Rapor Paneli", 
    layout="wide",
    initial_sidebar_state="collapsed" # Giriş yapana kadar yan menüyü gizle
)

# Tarayıcıların (Android/Windows) otomatik çeviri yapıp linki bozmasını engeller (Hata 404 çözümü)
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# Gelişmiş Responsive CSS: Tüm cihazlar için uyumlu tasarım ve kısıtlamalar
st.markdown("""
    <style>
    /* Metrik Kartları: Hem Light hem Dark modda rakamların okunmasını sağlar */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 12px;
    }
    
    /* Giriş Paneli: Tüm cihazlarda ortalar ve sığdırır */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 30px;
    }
    
    .login-box {
        max-width: 380px; 
        width: 100%;
        padding: 25px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 15px;
        background-color: transparent;
    }

    /* Mobilde grafiklerin taşmasını önler */
    .stPlotlyChart { width: 100% !important; }
    iframe { max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KULLANICI YETKİLERİ (Sözlük yapısı ile çoklu giriş) ---
KULLANICILAR = {
    "admin": "teknostore123",
    "pazarlama": "satis2026",
    "analiz": "rapor456"
}

# --- 3. VERİ TABANI SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026_final.csv'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        markalar = ['Teknostore', 'Aula', 'Nowgo']
        rows = []
        for m in markalar:
            for p in ['Instagram', 'Facebook', 'YouTube']:
                rows.append({
                    'Marka': m, 'Ay': 'Ocak 2026', 'Platform': p, 
                    'Takipci': 1000, 'Etkilesim': 1000, 'YT_Izlenme': 5000 if p == 'YouTube' else 0
                })
        df = pd.DataFrame(rows)
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

# --- 4. OTURUM YÖNETİMİ ---
if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False
if "aktif_kullanici" not in st.session_state:
    st.session_state.aktif_kullanici = ""

# --- 5. GİRİŞ EKRANI KONTROLÜ (GÖRSEL DÜZELTME YAPILDI) ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Boş Kolonlarla Ortalama
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        
        # TEKNOSTORE Yazısı veya Logosu
        if os.path.exists("logo.png"):
            st.image("logo.png", width=350)
        else:
            # Buradaki siyah dikdörtgen (Placeholder) kaldırıldı!
            # Yerine düzgün hizalanmış bir metin eklendi.
            st.markdown("<h1 style='text-align: center;'>TEKNOSTORE</h1>", unsafe_allow_html=True)
            
        # Giriş Kutusu (YÖNETİM GİRİŞİ)
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>🔐 Yönetim Girişi</h3>", unsafe_allow_html=True)
        
        # Input Alanları
        u = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınız...")
        p = st.text_input("Şifre", type="password", placeholder="Şifreniz...")
        
        # Giriş Butonu
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if u in KULLANICILAR and KULLANICILAR[u] == p:
                st.session_state.oturum_durumu = True
                st.session_state.aktif_kullanici = u
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 6. ANA ANALİZ PANELİ (Oturum Açık) ---
    df = veri_yukle()
    
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        st.info(f"👤 Kullanıcı: **{st.session_state.aktif_kullanici}**")
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            secilen_marka = st.selectbox("Marka Seçin:", df['Marka'].unique())
            secilen_ay = st.selectbox("Ay Seçin:", ["Ocak 2026", "Şubat 2026", "Mart 2026"])
        
        st.divider()
        with st.expander("🛠️ Veri Düzenle / Yeni Marka"):
            with st.form("admin_form"):
                f_secim = st.selectbox("Marka Seç", ["--- Yeni Marka Ekle ---"] + df['Marka'].unique().tolist())
                f_yeni_ad = st.text_input("Yeni Marka Adı (Eklenecekse)")
                f_ay = st.selectbox("Dönem", ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026"])
                ig_t = st.number_input("Instagram Takipçi", min_value=0)
                fb_t = st.number_input("Facebook Takipçi", min_value=0)
                yt_t = st.number_input("YouTube Takipçi", min_value=0)
                
                if st.form_submit_button("Güncelle"):
                    final_m = f_yeni_ad if f_secim == "--- Yeni Marka Ekle ---" else f_secim
                    if final_m:
                        df = df[~((df['Marka'] == final_m) & (df['Ay'] == f_ay))]
                        yeni_veriler = [
                            {'Marka': final_m, 'Ay': f_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Etkilesim': 1000},
                            {'Marka': final_m, 'Ay': f_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Etkilesim': 1000},
                            {'Marka': final_m, 'Ay': f_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Etkilesim': 1000}
                        ]
                        df = pd.concat([df, pd.DataFrame(yeni_veriler)], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.success("Başarıyla güncellendi!")
                        st.rerun()

        if st.button("Güvenli Çıkış", use_container_width=True):
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 7. RAPORLAMA EKRANI VE GRAFİKLER ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Tüm Markaların Genel Karşılaştırması")
        ozet = df.groupby('Marka')['Takipci'].sum().reset_index()
        fig = px.bar(ozet, x='Marka', y='Takipci', color='Marka', title="Toplam Marka Gücü")
        st.plotly_chart(fig, use_container_width=True)
    else:
        m_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)]
        st.title(f"📊 {secilen_marka} - {secilen_ay}")
        
        # Metrikler
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_df['Takipci'].sum()):,}")
        c2.metric("Toplam Etkileşim", f"{int(m_df['Etkilesim'].sum()):,}")
        c3.metric("Platform", secilen_marka)

        st.divider()
        col_l, col_r = st.columns([2, 1])
        with col_l:
            fig_bar = px.bar(m_df, x='Platform', y='Takipci', color='Platform',
                             color_discrete_map={'Instagram':'#E1306C', 'Facebook':'#4267B2', 'YouTube':'#FF0000'})
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_r:
            fig_pie = px.pie(m_df, values='Takipci', names='Platform', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
