import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Marka Yönetim Merkezi", layout="wide")

# --- VERİ TABANI SİMÜLASYONU (CSV) ---
# Eğer dosya yoksa örnek veriyle oluştur
if not os.path.exists('veriler.csv'):
    df_baslangic = pd.DataFrame({
        'Marka': ['Teknostore', 'Aula', 'Nowgo'],
        'Takipci': [15400, 8200, 19800],
        'Erisim': [42000, 18500, 76000],
        'Renk': ['#007bff', '#6f42c1', '#28a745']
    })
    df_baslangic.to_csv('veriler.csv', index=False)

df = pd.read_csv('veriler.csv')

# --- KULLANICI GİRİŞ SİSTEMİ ---
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.title("🔐 Marka Yönetim Paneli")
    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Sisteme Giriş Yap"):
        # Şimdilik basit şifre kontrolü (Geliştirilebilir)
        if kullanici == "admin" and sifre == "teknostore123":
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre!")
else:
    # --- ANA PANEL ---
    st.sidebar.success(f"Hoş geldin, {kullanici}!")
    sekme1, sekme2 = st.tabs(["📊 Analiz Dashboard", "➕ Marka/Veri Yönetimi"])

    with sekme1:
        st.title("📊 Canlı Performans Verileri")
        secilen_marka = st.selectbox("Analiz edilecek markayı seçin:", df['Marka'].tolist())
        
        m_verisi = df[df['Marka'] == secilen_marka].iloc[0]
        
        col1, col2 = st.columns(2)
        col1.metric("Toplam Takipçi", f"{m_verisi['Takipci']:,}")
        col2.metric("Aylık Erişim", f"{m_verisi['Erisim']:,}")
        
        fig = px.bar(df, x='Marka', y='Takipci', color='Marka', 
                     color_discrete_sequence=df['Renk'].tolist(), title="Marka Kıyaslaması")
    st.plotly_chart(fig, use_container_width=True)

    with sekme2:
        st.header("🛠 Yeni Marka Ekle veya Güncelle")
        with st.form("veri_formu"):
            m_ad = st.text_input("Marka Adı")
            m_takipci = st.number_input("Takipçi Sayısı", min_value=0)
            m_erisim = st.number_input("Erişim Sayısı", min_value=0)
            m_renk = st.color_picker("Grafik Rengi Seçin", "#000000")
            
            kaydet = st.form_submit_button("Veriyi Sisteme İşle")
            
            if kaydet:
                # Yeni veriyi ekle veya mevcut olanı güncelle
                yeni_satir = {'Marka': m_ad, 'Takipci': m_takipci, 'Erisim': m_erisim, 'Renk': m_renk}
                df = df[df.Marka != m_ad] # Varsa eskisini sil
                df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
                df.to_csv('veriler.csv', index=False)
                st.success(f"{m_ad} verileri başarıyla kaydedildi! Sayfayı yenileyebilirsiniz.")

    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.giris_yapildi = False
        st.rerun()
