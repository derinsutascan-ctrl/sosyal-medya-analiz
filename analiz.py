import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Marka Yönetim Merkezi", layout="wide")

# --- VERİ TABANI SİSTEMİ (CSV Dosyası) ---
# Verileri kalıcı olarak saklamak için CSV kullanıyoruz
DB_FILE = 'veriler.csv'

def verileri_yukle():
    if not os.path.exists(DB_FILE):
        # Dosya yoksa başlangıç verilerini oluştur
        baslangic_df = pd.DataFrame({
            'Marka': ['Teknostore', 'Aula', 'Nowgo'],
            'Takipci': [15400, 8200, 19800],
            'Erisim': [42000, 18500, 76000],
            'Renk': ['#007bff', '#6f42c1', '#28a745']
        })
        baslangic_df.to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE)

def verileri_kaydet(df):
    df.to_csv(DB_FILE, index=False)

# Verileri çek
df = verileri_yukle()

# --- GİRİŞ KONTROLÜ ---
if "giris_durumu" not in st.session_state:
    st.session_state.giris_durumu = False
    st.session_state.aktif_kullanici = ""

# --- GİRİŞ EKRANI ---
if not st.session_state.giris_durumu:
    st.title("🔐 Marka Yönetim Paneli")
    
    with st.container():
        user_input = st.text_input("Kullanıcı Adı")
        pass_input = st.text_input("Şifre", type="password")
        
        if st.button("Sisteme Giriş Yap"):
            # Örnek kullanıcılar (İleride bunu da CSV'den okutabiliriz)
            if user_input == "admin" and pass_input == "teknostore123":
                st.session_state.giris_durumu = True
                st.session_state.aktif_kullanici = "Yönetici"
                st.rerun()
            elif user_input == "ekip" and pass_input == "123456":
                st.session_state.giris_durumu = True
                st.session_state.aktif_kullanici = "Ekip Üyesi"
                st.rerun()
            else:
                st.error("Hatalı giriş! Lütfen tekrar deneyin.")

# --- ANA DASHBOARD (Giriş Yapıldıysa) ---
else:
    st.sidebar.title(f"👋 Hoş geldin, {st.session_state.aktif_kullanici}")
    
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.giris_durumu = False
        st.rerun()
    
    st.sidebar.divider()
    
    # SEKMELİ YAPI
    sekme1, sekme2 = st.tabs(["📊 Analiz Raporu", "🛠️ Veri & Marka Yönetimi"])

    with sekme1:
        st.title("📱 Sosyal Medya Performans Analizi")
        
        if not df.empty:
            secilen_marka = st.selectbox("Görüntülenecek Marka:", df['Marka'].unique())
            m_verisi = df[df['Marka'] == secilen_marka].iloc[0]
            
            # Üst Metrikler
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Takipçi", f"{int(m_verisi['Takipci']):,}")
            c2.metric("Aylık Erişim", f"{int(m_verisi['Erisim']):,}")
            c3.metric("Platform Rengi", m_verisi['Renk'])
            
            st.divider()
            
            # Karşılaştırma Grafiği
            fig = px.bar(df, x='Marka', y='Takipci', color='Marka', 
                         color_discrete_map=dict(zip(df['Marka'], df['Renk'])),
                         title="Markalar Arası Takipçi Kıyaslaması")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Henüz sisteme kayıtlı bir marka bulunamadı.")

    with sekme2:
        st.title("🛠️ Veri Düzenleme")
        
        with st.expander("➕ Yeni Marka Ekle / Mevcut Olanı Güncelle", expanded=True):
            with st.form("marka_ekleme_formu"):
                m_adi = st.text_input("Marka Adı (Örn: Teknostore)")
                m_taki = st.number_input("Takipçi Sayısı", min_value=0, step=1)
                m_eri = st.number_input("Erişim Sayısı", min_value=0, step=1)
                m_renk = st.color_picker("Grafik Rengi Seçin", "#1f77b4")
                
                if st.form_submit_button("Sisteme Kaydet"):
                    if m_adi:
                        # Eğer marka zaten varsa eskisini sil (Güncelleme mantığı)
                        df = df[df['Marka'] != m_adi]
                        yeni_satir = pd.DataFrame([[m_adi, m_taki, m_eri, m_renk]], 
                                                  columns=['Marka', 'Takipci', 'Erisim', 'Renk'])
                        df = pd.concat([df, yeni_satir], ignore_index=True)
                        verileri_kaydet(df)
                        st.success(f"✅ {m_adi} başarıyla güncellendi! Analiz sekmesine bakabilirsiniz.")
                        st.rerun()
                    else:
                        st.error("Lütfen bir marka adı girin.")

        with st.expander("🗑️ Marka Sil"):
            silinecek = st.selectbox("Silmek istediğiniz markayı seçin:", ["Seçiniz..."] + df['Marka'].tolist())
            if st.button("Markayı Sistemden Kaldır"):
                if silinecek != "Seçiniz...":
                    df = df[df['Marka'] != silinecek]
                    verileri_kaydet(df)
                    st.success(f"❌ {silinecek} başarıyla silindi.")
                    st.rerun()
