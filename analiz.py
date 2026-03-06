import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. AYARLAR VE TEMA ---
st.set_page_config(page_title="Teknostore Sosyal Medya Raporu", layout="wide")

# Şık Siyah Tema CSS
st.markdown("""
    <style>
    .stMetric { background-color: #1a1c23; border: 1px solid #343a40; padding: 15px; border-radius: 10px; }
    [data-testid="stSidebar"] { background-color: #111217; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (AYLIK YAPI) ---
DB_FILE = 'aylik_veriler.csv'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        # Örnek Başlangıç Verisi (Ocak 2026)
        data = {
            'Marka': ['Teknostore', 'Teknostore', 'Teknostore', 'Aula', 'Aula', 'Aula'],
            'Ay': ['Ocak 2026', 'Ocak 2026', 'Ocak 2026', 'Ocak 2026', 'Ocak 2026', 'Ocak 2026'],
            'Platform': ['Instagram', 'Facebook', 'YouTube', 'Instagram', 'Facebook', 'YouTube'],
            'Takipci': [12000, 5000, 3000, 8000, 4000, 1000],
            'Erisim': [35000, 12000, 8000, 20000, 9000, 3000]
        }
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE)

df = veri_yukle()

# --- 3. GİRİŞ SİSTEMİ ---
if "oturum" not in st.session_state:
    st.session_state.oturum = False

if not st.session_state.oturum:
    st.title("🔐 Yönetim Paneli Giriş")
    user = st.text_input("Kullanıcı")
    pw = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if user == "admin" and pw == "teknostore123":
            st.session_state.oturum = True
            st.rerun()
else:
    # --- 4. SOL MENÜ (SEÇİMLER) ---
    with st.sidebar:
        st.header("📍 Filtreler")
        secilen_marka = st.selectbox("Marka Seçin", df['Marka'].unique())
        secilen_ay = st.selectbox("Ay Seçin", df['Ay'].unique())
        
        st.divider()
        if st.button("Çıkış Yap"):
            st.session_state.oturum = False
            st.rerun()

    # --- 5. ANA SAYFA (GRAFİKLER) ---
    # Seçilen filtreye göre veriyi süz
    ekran_verisi = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)]
    
    st.title(f"📊 {secilen_marka} - {secilen_ay} Raporu")
    
    # Metrikler (Toplamlar)
    t_takipci = ekran_verisi['Takipci'].sum()
    t_erisim = ekran_verisi['Erisim'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Takipçi (Tüm Kanallar)", f"{t_takipci:,}")
    c2.metric("Toplam Erişim", f"{t_erisim:,}")
    c3.metric("Rapor Dönemi", secilen_ay)

    st.divider()

    # Sosyal Medya Dağılım Grafikleri
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Platform Bazlı Takipçi")
        fig_bar = px.bar(ekran_verisi, x='Platform', y='Takipci', color='Platform',
                         color_discrete_sequence=['#E1306C', '#4267B2', '#FF0000'], # IG, FB, YT renkleri
                         template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("Erişim Dağılımı (%)")
        fig_pie = px.pie(ekran_verisi, values='Erisim', names='Platform', hole=0.4,
                         color_discrete_sequence=['#E1306C', '#4267B2', '#FF0000'],
                         template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 6. VERİ GÜNCELLEME ALANI (EN ALTTA) ---
    st.divider()
    with st.expander("🛠️ Veri Girişi ve Güncelleme Paneli"):
        st.write("Yeni ay verisi girmek veya mevcut olanı değiştirmek için kullanın.")
        with st.form("güncelleme_formu"):
            f_marka = st.selectbox("Marka", ["Teknostore", "Aula", "Nowgo", "Yeni Ekle..."])
            f_yeni_marka = st.text_input("Yeni Marka Adı (Eğer listede yoksa)")
            f_ay = st.selectbox("Ay", ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026"])
            
            st.write("---")
            # Her platform için giriş alanları
            st.write("**Instagram**")
            ig_t = st.number_input("Instagram Takipçi", min_value=0)
            ig_e = st.number_input("Instagram Erişim", min_value=0)
            
            st.write("**Facebook**")
            fb_t = st.number_input("Facebook Takipçi", min_value=0)
            fb_e = st.number_input("Facebook Erişim", min_value=0)
            
            st.write("**YouTube**")
            yt_t = st.number_input("YouTube Takipçi", min_value=0)
            yt_e = st.number_input("YouTube Erişim", min_value=0)
            
            if st.form_submit_button("Verileri Kaydet"):
                hedef_marka = f_yeni_marka if f_marka == "Yeni Ekle..." else f_marka
                
                # Mevcut kayıtları temizle (tekrar yazmamak için)
                df = df[~((df['Marka'] == hedef_marka) & (df['Ay'] == f_ay))]
                
                # Yeni kayıtları ekle
                yeni_kayitlar = [
                    {'Marka': hedef_marka, 'Ay': f_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Erisim': ig_e},
                    {'Marka': hedef_marka, 'Ay': f_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Erisim': fb_e},
                    {'Marka': hedef_marka, 'Ay': f_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Erisim': yt_e}
                ]
                df = pd.concat([df, pd.DataFrame(yeni_kayitlar)], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success(f"{hedef_marka} için {f_ay} verileri güncellendi!")
                st.rerun()
