import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA AYARLARI VE TEMA UYUMLULUĞU ---
st.set_page_config(page_title="Teknostore Yönetim Paneli", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { min-width: 300px; max-width: 300px; }
    .stMetric { border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME (AYLIK VE PLATFORM BAZLI YAPI) ---
DB_FILE = 'aylik_veriler.csv'
if not os.path.exists(DB_FILE):
    # 2026 Ocak Başlangıç Verisi
    df = pd.DataFrame({
        'Marka': ['Teknostore', 'Teknostore', 'Teknostore', 'Aula', 'Aula', 'Aula', 'Nowgo', 'Nowgo', 'Nowgo'],
        'Ay': ['Ocak 2026'] * 9,
        'Platform': ['Instagram', 'Facebook', 'YouTube'] * 3,
        'Takipci': [12000, 2000, 1400, 6000, 1500, 700, 15000, 3000, 1800],
        'Erisim': [30000, 8000, 4000, 15000, 3000, 500, 60000, 10000, 6000],
        'Renk': ['#E1306C', '#4267B2', '#FF0000'] * 3 # Marka rengi yerine platform renkleri
    })
    df.to_csv(DB_FILE, index=False)
else:
    df = pd.read_csv(DB_FILE)

# --- 3. GİRİŞ SİSTEMİ ---
if "oturum" not in st.session_state:
    st.session_state.oturum = False

if not st.session_state.oturum:
    st.title("🔐 Giriş Yapın")
    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if kullanici == "admin" and sifre == "teknostore123":
            st.session_state.oturum = True
            st.rerun()
        else:
            st.error("Hatalı giriş!")
else:
    # --- 4. SOL MENÜ (SIDEBAR) ---
    with st.sidebar:
        st.title("🏢 Marka & Dönem")
        secilen_marka = st.selectbox("Marka seçin:", df['Marka'].unique())
        secilen_ay = st.selectbox("Ay seçin (2026+):", df['Ay'].unique())
        
        st.divider()
        
        st.title("🛠️ Veri Yönetimi")
        with st.expander("Aylık Veri Gir / Güncelle", expanded=False):
            with st.form("admin_form"):
                y_marka = st.selectbox("Marka", ["Teknostore", "Aula", "Nowgo"])
                y_ay = st.selectbox("Hangi Ay?", ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026"])
                
                st.write("**Instagram**")
                ig_t = st.number_input("Takipçi", key="ig_t", min_value=0)
                ig_e = st.number_input("Erişim", key="ig_e", min_value=0)
                
                st.write("**Facebook**")
                fb_t = st.number_input("Takipçi", key="fb_t", min_value=0)
                fb_e = st.number_input("Erişim", key="fb_e", min_value=0)
                
                st.write("**YouTube**")
                yt_t = st.number_input("Takipçi", key="yt_t", min_value=0)
                yt_e = st.number_input("Erişim", key="yt_e", min_value=0)
                
                if st.form_submit_button("Verileri Kaydet"):
                    # Önce o ayın eski verisini temizle
                    df = df[~((df['Marka'] == y_marka) & (df['Ay'] == y_ay))]
                    # Yeni platform verilerini ekle
                    yeni_veriler = pd.DataFrame([
                        {'Marka': y_marka, 'Ay': y_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Erisim': ig_e, 'Renk': '#E1306C'},
                        {'Marka': y_marka, 'Ay': y_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Erisim': fb_e, 'Renk': '#4267B2'},
                        {'Marka': y_marka, 'Ay': y_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Erisim': yt_e, 'Renk': '#FF0000'}
                    ])
                    df = pd.concat([df, yeni_veriler], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Veriler Kaydedildi!")
                    st.rerun()
        
        st.divider()
        if st.sidebar.button("Güvenli Çıkış"):
            st.session_state.oturum = False
            st.rerun()

    # --- 5. ANA EKRAN (GRAFİKLER) ---
    # Seçilen marka ve aya göre veriyi filtrele
    m_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)]
    
    if not m_df.empty:
        st.title(f"📊 {secilen_marka} Performans Raporu")
        st.subheader(f"📅 Dönem: {secilen_ay}")
        
        # Metrik Kartları
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi (Tüm Kanallar)", f"{int(m_df['Takipci'].sum()):,}")
        c2.metric("Toplam Erişim", f"{int(m_df['Erisim'].sum()):,}")
        c3.metric("Seçili Marka", secilen_marka)

        st.divider()

        # Grafikler
        col_sol, col_sag = st.columns([2, 1])
        
        with col_sol:
            st.subheader("Platform Bazlı Takipçi Dağılımı")
            fig = px.bar(m_df, x='Platform', y='Takipci', color='Platform', 
                         color_discrete_map={'Instagram': '#E1306C', 'Facebook': '#4267B2', 'YouTube': '#FF0000'})
            st.plotly_chart(fig, use_container_width=True)

        with col_sag:
            st.subheader("Erişim Paylaşımı (%)")
            fig_pie = px.pie(m_df, values='Erisim', names='Platform', hole=0.4,
                             color_discrete_map={'Instagram': '#E1306C', 'Facebook': '#4267B2', 'YouTube': '#FF0000'})
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning(f"{secilen_ay} dönemi için henüz veri girişi yapılmamış.")
