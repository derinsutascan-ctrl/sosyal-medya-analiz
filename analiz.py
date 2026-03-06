import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide")

# CSS: Logoyu ortalar ve metriklerin her iki modda (aydınlık/karanlık) okunmasını sağlar
st.markdown("""
    <style>
    /* Metrik Kartları: Arka planı yumuşak gri yaparak yazıların okunmasını sağlar */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 20px;
        border-radius: 15px;
    }
    
    /* Giriş Paneli ve Logo Konumu */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 30px;
    }
    
    .login-box {
        width: 400px;
        padding: 30px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026.csv'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        markalar = ['Teknostore', 'Aula', 'Nowgo']
        rows = []
        for m in markalar:
            for p in ['Instagram', 'Facebook', 'YouTube']:
                rows.append({'Marka': m, 'Ay': 'Ocak 2026', 'Platform': p, 'Takipci': 1000, 'Erisim': 1000})
        df = pd.DataFrame(rows)
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

# --- 3. OTURUM YÖNETİMİ ---
if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False

# --- 4. GİRİŞ EKRANI (TAM İSTEDİĞİN GÖRSEL DÜZEN) ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Logo Dosyası (Aynı klasörde logo.png olmalı)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=400)
    else:
        st.title("TEKNOSTORE")
    
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("🔐 Yönetim Girişi")
        user = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınız...")
        pw = st.text_input("Şifre", type="password", placeholder="Şifreniz...")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if user == "admin" and pw == "teknostore123":
                st.session_state.oturum_durumu = True
                st.rerun()
            else:
                st.error("Giriş bilgileri hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL ---
    df = veri_yukle()
    
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        st.divider()
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            secilen_marka = st.selectbox("Marka Seçin:", df['Marka'].unique())
            secilen_ay = st.selectbox("Ay Seçin:", ["Ocak 2026", "Şubat 2026", "Mart 2026"])
        
        st.divider()
        with st.expander("🛠️ Veri Düzenle / Yeni Marka"):
            with st.form("admin_form"):
                f_marka = st.text_input("Marka Adı", value=secilen_marka if 'secilen_marka' in locals() else "")
                f_ay = st.selectbox("Dönem", ["Ocak 2026", "Şubat 2026", "Mart 2026"])
                ig_t = st.number_input("Instagram Takipçi", min_value=0, format="%d")
                fb_t = st.number_input("Facebook Takipçi", min_value=0, format="%d")
                yt_t = st.number_input("YouTube Takipçi", min_value=0, format="%d")
                
                if st.form_submit_button("Güncelle ve Kaydet"):
                    df = df[~((df['Marka'] == f_marka) & (df['Ay'] == f_ay))]
                    yeni_data = [
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Erisim': 1000},
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Erisim': 1000},
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Erisim': 1000}
                    ]
                    df = pd.concat([df, pd.DataFrame(yeni_data)], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Veriler kaydedildi!")
                    st.rerun()

        if st.button("Güvenli Çıkış", use_container_width=True):
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. RAPORLAMA EKRANI ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Markaların Genel Durumu")
        ozet = df.groupby('Marka')['Takipci'].sum().reset_index()
        fig = px.bar(ozet, x='Marka', y='Takipci', color='Marka', title="Toplam Marka Gücü")
        st.plotly_chart(fig, use_container_width=True)
    else:
        m_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)]
        st.title(f"📊 {secilen_marka} Analizi")
        
        # Metrikler (Dinamik Renkli)
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_df['Takipci'].sum()):,}")
        c2.metric("Ortalama Erişim", f"{int(m_df['Erisim'].mean()):,}")
        c3.metric("Platform", secilen_marka)

        st.divider()
        l, r = st.columns([2, 1])
        with l:
            st.subheader("Kanal Bazlı Takipçi")
            fig_bar = px.bar(m_df, x='Platform', y='Takipci', color='Platform',
                             color_discrete_map={'Instagram':'#E1306C', 'Facebook':'#4267B2', 'YouTube':'#FF0000'})
            st.plotly_chart(fig_bar, use_container_width=True)
        with r:
            st.subheader("Takipçi Dağılımı")
            fig_pie = px.pie(m_df, values='Takipci', names='Platform', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
