import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(
    page_title="Teknostore Rapor Paneli", 
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# Tarayıcı çeviri hatalarını (404) önler
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# CSS: Formu yukarı çeker, dikdörtgeni siler ve iç sayfa tasarımını korur
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        margin-top: 20px;
    }
    .login-box {
        max-width: 360px; 
        width: 100%;
        padding: 25px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026_final.csv'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        # Varsayılan boş bir yapı oluşturur
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Platform', 'Takipci', 'Etkilesim', 'YT_Izlenme'])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)
# --- 3. KULLANICI YETKİLERİ ---
KULLANICILAR = {
    "admin": "teknostore123",
    "pazarlama": "satis2026",
    "analiz": "rapor456"
}

if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False
if "aktif_kullanici" not in st.session_state:
    st.session_state.aktif_kullanici = ""

# --- 4. GİRİŞ EKRANI (DÜZENLENMİŞ) ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    # Dikdörtgeni kaldıran kontrol: Sadece dosya varsa çalışır
    if os.path.exists("logo.png"):
        st.image("logo.png", width=250)
    
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0;'>🔐 Yönetim Girişi</h3>", unsafe_allow_html=True)
        
        u = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınız...")
        p = st.text_input("Şifre", type="password", placeholder="Şifreniz...")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if u in KULLANICILAR and KULLANICILAR[u] == p:
                st.session_state.oturum_durumu = True
                st.session_state.aktif_kullanici = u
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL (SENİN KODUNUN DEVAMI) ---
    df = veri_yukle()
    
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        st.info(f"👤 Kullanıcı: {st.session_state.aktif_kullanici}") # Kimin girdiğini gösterir
        
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            secilen_marka = st.selectbox("Marka Seçin:", df['Marka'].unique())
            secilen_ay = st.selectbox("Ay Seçin:", df['Ay'].unique())
        
        st.divider()
        with st.expander("🛠️ Yeni Marka / Veri Güncelle"):
            with st.form("admin_form"):
                f_secim = st.selectbox("Marka Seç", ["--- Yeni Marka Ekle ---"] + df['Marka'].unique().tolist())
                f_yeni_ad = st.text_input("Yeni Marka Adı (Eklenecekse)")
                f_ay = st.selectbox("Dönem", ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026"])
                f_plat = st.selectbox("Platform", ["Instagram", "Facebook", "YouTube"])
                f_takipci = st.number_input("Takipçi Sayısı", min_value=0)
                f_etkilesim = st.number_input("Etkileşim Sayısı", min_value=0)
                f_izlenme = st.number_input("YT İzlenme (Sadece YouTube)", min_value=0)
                
                if st.form_submit_button("Sisteme Kaydet"):
                    final_m = f_yeni_ad if f_secim == "--- Yeni Marka Ekle ---" else f_secim
                    if final_m:
                        df = df[~((df['Marka'] == final_m) & (df['Ay'] == f_ay) & (df['Platform'] == f_plat))]
                        yeni = {'Marka': final_m, 'Ay': f_ay, 'Platform': f_plat, 'Takipci': f_takipci, 'Etkilesim': f_etkilesim, 'YT_Izlenme': f_izlenme}
                        df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.success(f"{final_m} verisi işlendi!")
                        st.rerun()

        if st.button("Güvenli Çıkış", use_container_width=True):
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. RAPORLAMA VE GRAFİKLER ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Tüm Markaların Genel Trendi")
        trend_df = df.groupby(['Ay', 'Marka'])['Takipci'].sum().reset_index()
        fig_trend = px.line(trend_df, x='Ay', y='Takipci', color='Marka', markers=True, title="Aylık Toplam Takipçi Değişimi")
        st.plotly_chart(fig_trend, use_container_width=True)
        
    else:
        m_df = df[df['Marka'] == secilen_marka]
        m_ay_df = m_df[m_df['Ay'] == secilen_ay]
        
        st.title(f"📊 {secilen_marka} Performans Analizi")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_ay_df['Takipci'].sum()):,}")
        c2.metric("Toplam Etkileşim", f"{int(m_ay_df['Etkilesim'].sum()):,}")
        c3.metric("Seçilen Ay", secilen_ay)

        st.divider()
        st.subheader("📈 Aylık Gelişim Trendleri")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            fig1 = px.area(m_df.groupby('Ay')['Takipci'].sum().reset_index(), x='Ay', y='Takipci', title="Takipçi Trendi", color_discrete_sequence=['#FF4B4B'])
            st.plotly_chart(fig1, use_container_width=True)
        with col_t2:
            fig2 = px.line(m_df.groupby('Ay')['Etkilesim'].sum().reset_index(), x='Ay', y='Etkilesim', title="Etkileşim Trendi", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            st.subheader("🎥 YouTube İzlenme Analizi")
            yt_data = m_df[m_df['Platform'] == 'YouTube']
            if not yt_data.empty:
                fig_yt = px.bar(yt_data, x='Ay', y='YT_Izlenme', title="Aylık YouTube İzlenme Sayıları", color='YT_Izlenme', color_continuous_scale='Reds')
                st.plotly_chart(fig_yt, use_container_width=True)
            else:
                st.info("YouTube verisi bulunamadı.")
        
        with col_b2:
            st.subheader("🥧 Platform Dağılımı")
            fig_pie = px.pie(m_ay_df, values='Takipci', names='Platform', hole=0.4, title=f"{secilen_ay} Takipçi Payı")
            st.plotly_chart(fig_pie, use_container_width=True)
