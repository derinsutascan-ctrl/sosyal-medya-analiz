import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Admin Panel", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #111; border: 1px solid #333; padding: 15px; border-radius: 10px; }
    [data-testid="stSidebar"] { min-width: 300px; }
    /* Giriş kutusunu ortalayan stil */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 100px;
    }
    .login-box {
        width: 350px;
        padding: 30px;
        border: 1px solid #333;
        border-radius: 15px;
        background: #0e1117;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI SİSTEMİ (Hazır 1000 değerleri ile) ---
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

# --- 4. GİRİŞ EKRANI (KÜÇÜK VE ORTALI) ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    with st.container():
        _, col_mid, _ = st.columns([1, 2, 1])
        with col_mid:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.subheader("🔐 Yönetim Girişi")
            user = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınız...")
            pw = st.text_input("Şifre", type="password", placeholder="Şifreniz...")
            if st.button("Giriş Yap", use_container_width=True):
                if user == "admin" and pw == "teknostore123":
                    st.session_state.oturum_durumu = True
                    st.rerun()
                else:
                    st.error("Hatalı bilgiler!")
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL ---
    df = veri_yukle()
    
    with st.sidebar:
        st.title("🚀 Menü")
        # Sayfa Seçimi
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        st.divider()
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            secilen_marka = st.selectbox("Marka Seçin:", df['Marka'].unique())
            secilen_ay = st.selectbox("Ay Seçin:", ["Ocak 2026", "Şubat 2026", "Mart 2026"])
        
        st.divider()
        
        # VERİ GÜNCELLEME ALANI
        st.subheader("🛠️ Veri & Marka Yönetimi")
        with st.expander("Veri Düzenle / Yeni Marka"):
            with st.form("admin_form"):
                mevcut_m = ["--- Yeni Marka Ekle ---"] + df['Marka'].unique().tolist()
                f_secim = st.selectbox("Marka Seç", mevcut_m)
                f_yeni_ad = st.text_input("Yeni Marka Adı (Eklenecekse)")
                f_ay = st.selectbox("Dönem", ["Ocak 2026", "Şubat 2026", "Mart 2026"])
                
                st.write("**Rakamları Girin:**")
                ig_t = st.number_input("Instagram Takipçi", min_value=0, step=1)
                fb_t = st.number_input("Facebook Takipçi", min_value=0, step=1)
                yt_t = st.number_input("YouTube Takipçi", min_value=0, step=1)
                
                if st.form_submit_button("Sisteme İşle"):
                    final_m = f_yeni_ad if f_secim == "--- Yeni Marka Ekle ---" else f_secim
                    if final_m:
                        # Eskileri sil
                        df = df[~((df['Marka'] == final_m) & (df['Ay'] == f_ay))]
                        # Yenileri ekle
                        yeni_satirlar = [
                            {'Marka': final_m, 'Ay': f_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Erisim': 1000},
                            {'Marka': final_m, 'Ay': f_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Erisim': 1000},
                            {'Marka': final_m, 'Ay': f_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Erisim': 1000}
                        ]
                        df = pd.concat([df, pd.DataFrame(yeni_satirlar)], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.success(f"{final_m} Güncellendi!")
                        st.rerun()

        if st.button("Güvenli Çıkış", use_container_width=True):
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. GÖRÜNTÜLEME ALANI ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Markaların Genel Karşılaştırması")
        # Grafik için veriyi hazırla
        genel_df = df.groupby('Marka')['Takipci'].sum().reset_index()
        fig_genel = px.bar(genel_df, x='Marka', y='Takipci', color='Marka', 
                           title="Toplam Takipçi Gücü", template="plotly_dark")
        st.plotly_chart(fig_genel, use_container_width=True)

    else:
        # Marka Bazlı Detay
        m_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)]
        
        st.title(f"📊 {secilen_marka} - {secilen_ay} Analizi")
        
        # Metrikler
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_df['Takipci'].sum()):,}")
        c2.metric("Ortalama Erişim", f"{int(m_df['Erisim'].mean()):,}")
        c3.metric("Platform", secilen_marka)

        st.divider()

        # Grafikler
        l, r = st.columns([2, 1])
        with l:
            st.subheader("Kanal Bazlı Takipçi")
            fig = px.bar(m_df, x='Platform', y='Takipci', color='Platform',
                         color_discrete_map={'Instagram':'#E1306C', 'Facebook':'#4267B2', 'YouTube':'#FF0000'},
                         template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        with r:
            st.subheader("Dağılım")
            fig_p = px.pie(m_df, values='Takipci', names='Platform', hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_p, use_container_width=True)
