import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide")

# Dinamik Tema CSS: Logoyu ortalar ve aydınlık moddaki metrik sorunlarını çözer
st.markdown("""
    <style>
    /* Metrik Kartları: Hem Light hem Dark modda yazılar net görünür */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 20px;
        border-radius: 15px;
    }
    
    /* Giriş Paneli Tasarımı */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 50px;
    }
    
    /* Logo Stil Ayarı */
    .logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 350px;
        margin-bottom: -20px;
    }

    /* Giriş Kutusu */
    .login-box {
        width: 400px;
        padding: 40px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 15px;
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

# --- 4. GİRİŞ EKRANI (TAM İSTEDİĞİN GİBİ) ---
if not st.session_state.oturum_durumu:
    # Logo ve Formu Ortalayan Alan
    _, col_mid, _ = st.columns([1, 2, 1])
    
    with col_mid:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        # Logo Dosyası Kontrolü
        if os.path.exists("logo.png"):
            st.image("logo.png", width=350)
        else:
            st.title("TEKNOSTORE")
            
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("🔐 Yönetim Girişi")
        user = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınız...")
        pw = st.text_input("Şifre", type="password", placeholder="Şifreniz...")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if user == "admin" and pw == "teknostore123":
                st.session_state.oturum_durumu = True
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
        st.markdown('</div></div>', unsafe_allow_html=True)

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
                ig_t = st.number_input("Instagram Takipçi", min_value=0)
                fb_t = st.number_input("Facebook Takipçi", min_value=0)
                yt_t = st.number_input("YouTube Takipçi", min_value=0)
                
                if st.form_submit_button("Verileri Kaydet"):
                    df = df[~((df['Marka'] == f_marka) & (df['Ay'] == f_ay))]
                    yeni_v = [
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Erisim': 1000},
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Erisim': 1000},
                        {'Marka': f_marka, 'Ay': f_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Erisim': 1000}
                    ]
                    df = pd.concat([df, pd.DataFrame(yeni_v)], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Veriler güncellendi!")
                    st.rerun()

        if st.button("Güvenli Çıkış", use_container_width=True):
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. RAPORLAMA ALANI ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Markaların Genel Karşılaştırması")
        genel_df = df.groupby('Marka')['Takipci'].sum().reset_index()
        fig = px.bar(genel_df, x='Marka', y='Takipci', color='Marka', 
                    title="Toplam Takipçi Sayıları (Mecra Bağımsız)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        m_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)]
        st.title(f"📊 {secilen_marka} - {secilen_ay} Analizi")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_df['Takipci'].sum()):,}")
        c2.metric("Ortalama Erişim", f"{int(m_df['Erisim'].mean()):,}")
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
