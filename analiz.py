import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA AYARLARI (İLK TASARIMDAKİ GİBİ) ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide")

# Sevdiğin Karanlık Tema CSS
st.markdown("""
    <style>
    .stMetric { background-color: #111; border: 1px solid #333; padding: 15px; border-radius: 10px; }
    [data-testid="stSidebar"] { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
DB_FILE = 'aylik_veriler.csv'
if not os.path.exists(DB_FILE):
    # Ocak 2026 Başlangıç Verileri
    data = {
        'Marka': ['Teknostore', 'Teknostore', 'Teknostore', 'Aula', 'Aula', 'Aula', 'Nowgo', 'Nowgo', 'Nowgo'],
        'Ay': ['Ocak 2026'] * 9,
        'Platform': ['Instagram', 'Facebook', 'YouTube'] * 3,
        'Takipci': [15400, 5200, 3100, 8200, 4100, 1200, 19800, 7500, 4200],
        'Erisim': [42000, 15000, 8000, 18500, 9000, 2500, 76000, 22000, 11000]
    }
    df = pd.DataFrame(data)
    df.to_csv(DB_FILE, index=False)
else:
    df = pd.read_csv(DB_FILE)

# --- 3. GİRİŞ KONTROLÜ ---
if "oturum" not in st.session_state:
    st.session_state.oturum = False

if not st.session_state.oturum:
    st.title("🔐 Giriş Yapın")
    u = st.text_input("Kullanıcı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if u == "admin" and p == "teknostore123":
            st.session_state.oturum = True
            st.rerun()
else:
    # --- 4. SOL MENÜ (SEÇİMLER) ---
    with st.sidebar:
        st.title("📂 Menü")
        secilen_marka = st.selectbox("Marka Seçin:", df['Marka'].unique())
        secilen_ay = st.selectbox("Dönem Seçin:", df['Ay'].unique())
        st.divider()
        if st.button("Güvenli Çıkış"):
            st.session_state.oturum = False
            st.rerun()

    # --- 5. ANA SAYFA (TAMAMEN SENİN İSTEDİĞİN DÜZEN) ---
    ekran_verisi = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)]
    
    # Başlık
    st.title(f"📊 {secilen_marka} Sosyal Medya Raporu ({secilen_ay})")
    
    # Üst Metrik Kartları (İlk görseldeki gibi 4'lü yapı)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Takipçi", f"{ekran_verisi['Takipci'].sum():,}", "+5%")
    c2.metric("Aylık Erişim", f"{ekran_verisi['Erisim'].sum():,}", "+12%")
    c3.metric("Etkileşim Oranı", "%4.8", "0.3%")
    c4.metric("Aktif Reklam", "4 Adet", "Sabit")

    st.divider()

    # Grafikler
    col_sol, col_sag = st.columns([2, 1])
    
    with col_sol:
        st.subheader("Platform Bazlı Etkileşim")
        fig = px.bar(ekran_verisi, x='Platform', y='Takipci', color='Platform',
                     color_discrete_map={'Instagram': '#E1306C', 'Facebook': '#4267B2', 'YouTube': '#FF0000'},
                     template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col_sag:
        st.subheader("Kanal Dağılımı (%)")
        fig_pie = px.pie(ekran_verisi, values='Takipci', names='Platform', hole=0.4,
                         color_discrete_map={'Instagram': '#E1306C', 'Facebook': '#4267B2', 'YouTube': '#FF0000'},
                         template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 6. GİZLİ YÖNETİM PANELİ (EN ALTA EKLENDİ) ---
    st.divider()
    with st.expander("🛠️ Veri Güncelleme ve Aylık Giriş Alanı"):
        with st.form("aylik_guncelleme"):
            st.write(f"**{secilen_marka}** markası için veri giriyorsunuz.")
            f_ay = st.selectbox("Hangi Ay?", ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026"])
            
            st.info("Instagram Verileri")
            ig_t = st.number_input("Instagram Takipçi", value=0)
            ig_e = st.number_input("Instagram Erişim", value=0)
            
            st.info("Facebook Verileri")
            fb_t = st.number_input("Facebook Takipçi", value=0)
            fb_e = st.number_input("Facebook Erişim", value=0)
            
            st.info("YouTube Verileri")
            yt_t = st.number_input("YouTube Takipçi", value=0)
            yt_e = st.number_input("YouTube Erişim", value=0)
            
            if st.form_submit_button("Verileri Sisteme İşle"):
                # Eskileri sil, yenileri ekle
                df = df[~((df['Marka'] == secilen_marka) & (df['Ay'] == f_ay))]
                yeni = pd.DataFrame([
                    {'Marka': secilen_marka, 'Ay': f_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Erisim': ig_e},
                    {'Marka': secilen_marka, 'Ay': f_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Erisim': fb_e},
                    {'Marka': secilen_marka, 'Ay': f_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Erisim': yt_e}
                ])
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("Veriler kaydedildi! Lütfen sayfayı yenileyin veya ayı seçin.")
                st.rerun()
