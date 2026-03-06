import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide")

# Dinamik Tema CSS (Hem aydınlık hem karanlık moda tam uyum)
st.markdown("""
    <style>
    /* Metrik Kartları: Arka planı şeffaf yaparak sistem temasına uydurur */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 12px;
    }
    
    /* Giriş Paneli Tasarımı */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 50px;
    }
    
    .login-box {
        width: 380px;
        padding: 30px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Logo Boyutu */
    .brand-logo {
        width: 300px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026.csv'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        markalar = ['Teknostore', 'Aula', 'Nowgo']
        platformlar = ['Instagram', 'Facebook', 'YouTube']
        rows = []
        for m in markalar:
            for p in platformlar:
                rows.append({'Marka': m, 'Ay': 'Ocak 2026', 'Platform': p, 'Takipci': 1000, 'Erisim': 1000})
        df = pd.DataFrame(rows)
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

# --- 3. OTURUM YÖNETİMİ ---
if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False

# --- 4. GİRİŞ EKRANI (LOGOLU) ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # GÖNDERDİĞİN LOGO BURAYA GELİYOR
    # Not: logo.png dosyasının kodla aynı klasörde olduğundan emin ol!
    if os.path.exists("logo.png"):
        st.image("logo.png", width=350)
    else:
        st.title("TEKNOSTORE") # Logo yoksa yazı görünür
        
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("🔐 Yönetim Girişi")
        user = st.text_input("Kullanıcı Adı", key="user_input")
        pw = st.text_input("Şifre", type="password", key="pw_input")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if user == "admin" and pw == "teknostore123":
                st.session_state.oturum_durumu = True
                st.rerun()
            else:
                st.error("Hatalı bilgiler!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL (OTURUM AÇIK) ---
    df = veri_yukle()
    
    with st.sidebar:
        # Sidebar'ın en üstüne de küçük bir logo
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
            
        st.title("🚀 Menü")
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            marka_listesi = df['Marka'].unique().tolist()
            secilen_marka = st.selectbox("Marka Seçin:", marka_listesi)
            secilen_ay = st.selectbox("Ay Seçin:", df['Ay'].unique())
        
        st.divider()
        with st.expander("🛠️ Veri Düzenle / Yeni Marka"):
            with st.form("admin_form"):
                f_marka = st.text_input("Marka Adı", value=secilen_marka if 'secilen_marka' in locals() else "")
                f_ay = st.selectbox("Dönem", ["Ocak 2026", "Şubat 2026", "Mart 2026"])
                ig_t = st.number_input("Instagram Takipçi", min_value=0, format="%d")
                fb_t = st.number_input("Facebook Takipçi", min_value=0, format="%d")
                yt_t = st.number_input("YouTube Takipçi", min_value=0, format="%d")
                
                if st.form_submit_button("Güncelle"):
                    df = df[~((df['Marka'] == f_marka) & (df['Ay'] == f_ay))]
                    yeni_veriler = [
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Erisim': 1000},
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Erisim': 1000},
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Erisim': 1000}
                    ]
                    df = pd.concat([df, pd.DataFrame(yeni_veriler)], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Başarıyla kaydedildi!")
                    st.rerun()

        if st.button("Güvenli Çıkış", use_container_width=True):
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. GÖRÜNTÜLEME ALANI
