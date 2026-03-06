import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA AYARLARI VE TEMA UYUMLULUĞU ---
st.set_page_config(page_title="Teknostore Yönetim Paneli", layout="wide")

# Sistem temasına (Karanlık/Aydınlık) tam uyum için CSS
st.markdown("""
    <style>
    [data-testid="stSidebar"] { min-width: 300px; max-width: 300px; }
    .stMetric { border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME ---
DB_FILE = 'veriler.csv'
if not os.path.exists(DB_FILE):
    df = pd.DataFrame({
        'Marka': ['Teknostore', 'Aula', 'Nowgo'],
        'Takipci': [15400, 8200, 19800],
        'Erisim': [42000, 18500, 76000],
        'Renk': ['#007bff', '#6f42c1', '#28a745']
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
    # --- 4. SOL MENÜ (SIDEBAR) - TÜM KONTROLLER BURADA ---
    with st.sidebar:
        st.title("🏢 Marka Seçimi")
        secilen_marka = st.selectbox("Analiz edilecek markayı seçin:", df['Marka'].tolist())
        
        st.divider()
        
        st.title("🛠️ Veri Yönetimi")
        with st.expander("Veri Güncelle / Yeni Marka", expanded=False):
            with st.form("admin_form"):
                y_marka = st.text_input("Marka Adı", value=secilen_marka)
                y_takipci = st.number_input("Takipçi Sayısı", value=0)
                y_erisim = st.number_input("Aylık Erişim", value=0)
                y_renk = st.color_picker("Grafik Rengi", "#007bff")
                
                if st.form_submit_button("Kaydet ve Güncelle"):
                    yeni_df = df[df['Marka'] != y_marka]
                    yeni_satir = pd.DataFrame([{'Marka': y_marka, 'Takipci': y_takipci, 'Erisim': y_erisim, 'Renk': y_renk}])
                    df = pd.concat([yeni_df, yeni_satir], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Veri Kaydedildi!")
                    st.rerun()
        
        st.divider()
        if st.sidebar.button("Güvenli Çıkış"):
            st.session_state.oturum = False
            st.rerun()

    # --- 5. ANA EKRAN (GRAFİKLER) ---
    m = df[df['Marka'] == secilen_marka].iloc[0]

    st.title(f"📊 {secilen_marka} Performans Raporu")
    
    # Metrik Kartları
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Takipçi", f"{int(m['Takipci']):,}")
    c2.metric("Aylık Erişim", f"{int(m['Erisim']):,}")
    c3.metric("Platform", secilen_marka)

    st.divider()

    # Grafikler - Otomatik Tema Uyumluluğu
    col_sol, col_sag = st.columns([2, 1])
    
    with col_sol:
        st.subheader("Marka Karşılaştırması")
        fig = px.bar(df, x='Marka', y='Takipci', color='Marka', 
                     color_discrete_map=dict(zip(df['Marka'], df['Renk'])))
        st.plotly_chart(fig, use_container_width=True)

    with col_sag:
        st.subheader("Takipçi Dağılımı")
        fig_pie = px.pie(df, values='Takipci', names='Marka', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
