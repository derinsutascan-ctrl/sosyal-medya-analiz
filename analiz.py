import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA AYARLARI (İLK TASARIMDAKİ GİBİ) ---
st.set_page_config(page_title="Teknostore Analiz Paneli", page_icon="📊", layout="wide")

# Arka planı koyu ve şık yapan CSS (Senin sevdiğin stil)
st.markdown("""
    <style>
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    div[data-testid="stExpander"] { border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
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

# --- 3. GİRİŞ EKRANI SİSTEMİ ---
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
    # --- 4. ANA SAYFA (SENİN SEVDİĞİN GRAFİK ALANI) ---
    
    # Sol Menü (Sidebar)
    st.sidebar.title("🏢 Marka Seçimi")
    secilen_marka = st.sidebar.selectbox("Lütfen bir marka seçin:", df['Marka'].tolist())
    
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.oturum = False
        st.rerun()

    # Veriyi çek
    m = df[df['Marka'] == secilen_marka].iloc[0]

    st.title(f"📊 {secilen_marka} Sosyal Medya Raporu")
    
    # Özet Kartları (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Takipçi", f"{int(m['Takipci']):,}", "+5%")
    c2.metric("Aylık Erişim", f"{int(m['Erisim']):,}", "+12%")
    c3.metric("Etkileşim Oranı", "%4.8", "0.3%")
    c4.metric("Aktif Reklam", "4 Adet", "Sabit")

    st.divider()

    # Grafikler
    col_sol, col_sag = st.columns([2, 1])
    
    with col_sol:
        st.subheader("Platform Performansı")
        fig = px.bar(df, x='Marka', y='Takipci', color='Marka', 
                     color_discrete_map=dict(zip(df['Marka'], df['Renk'])),
                     template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col_sag:
        st.subheader("Dağılım")
        fig_pie = px.pie(df, values='Takipci', names='Marka', hole=0.4, template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 5. YÖNETİM ALANI (SAYFANIN EN ALTINDA, GİZLENEBİLİR) ---
    st.divider()
    with st.expander("🛠️ Veri Düzenleme ve Yeni Marka Ekleme Paneli"):
        st.info("Buradan yeni markalar ekleyebilir veya mevcut sayıları güncelleyebilirsiniz.")
        with st.form("admin_form"):
            y_marka = st.text_input("Marka Adı")
            y_takipci = st.number_input("Takipçi", min_value=0)
            y_erisim = st.number_input("Erişim", min_value=0)
            y_renk = st.color_picker("Renk", m['Renk'])
            
            if st.form_submit_button("Kaydet ve Yayınla"):
                yeni_df = df[df['Marka'] != y_marka] # Varsa eskisini güncellemek için sil
                yeni_satir = pd.DataFrame([{'Marka': y_marka, 'Takipci': y_takipci, 'Erisim': y_erisim, 'Renk': y_renk}])
                df = pd.concat([yeni_df, yeni_satir], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("Veriler başarıyla güncellendi!")
                st.rerun()
