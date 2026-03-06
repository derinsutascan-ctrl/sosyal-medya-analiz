import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(
    page_title="Teknostore Rapor Paneli", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Tarayıcıların (Android/Windows) otomatik çeviri yapıp linki bozmasını engeller
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# Gelişmiş Responsive CSS
st.markdown("""
    <style>
    /* Metrik Kartları: Yazıların her modda okunmasını sağlar */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 12px;
    }
    
    /* Giriş Paneli: Tüm cihazlarda ortalar ve sığdırır */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 30px;
    }
    
    .login-box {
        max-width: 400px;
        width: 100%;
        padding: 25px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 15px;
        background-color: transparent;
    }

    /* Mobilde grafiklerin taşmasını önler */
    .stPlotlyChart { width: 100% !important; }
    iframe { max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026_final.csv'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        markalar = ['Teknostore', 'Aula', 'Nowgo']
        aylar = ['Ocak 2026', 'Şubat 2026', 'Mart 2026']
        rows = []
        for m in markalar:
            for a in aylar:
                for p in ['Instagram', 'Facebook', 'YouTube']:
                    rows.append({
                        'Marka': m, 'Ay': a, 'Platform': p, 
                        'Takipci': 1000, 'Etkilesim': 100, 
                        'YT_Izlenme': 500 if p == 'YouTube' else 0
                    })
        df = pd.DataFrame(rows)
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

# --- 3. KULLANICI YETKİLERİ ---
# Buraya dilediğin kadar kullanıcı ekleyebilirsin
KULLANICILAR = {
    "admin": "teknostore123",
    "pazarlama": "satis2026",
    "analiz": "rapor456",
    "yonetim": "tekno789"
}

if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False
if "aktif_kullanici" not in st.session_state:
    st.session_state.aktif_kullanici = ""

# --- 4. GİRİŞ EKRANI GÜNCELLEMESİ ---
if not st.session_state.oturum_durumu:
    # ... (Logo ve Login Box kısımları aynı kalıyor) ...
    
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap", use_container_width=True):
        # Kullanıcı sözlükte var mı ve şifre doğru mu kontrolü
        if u in KULLANICILAR and KULLANICILAR[u] == p:
            st.session_state.oturum_durumu = True
            st.session_state.aktif_kullanici = u
            st.success(f"Hoş geldiniz, {u.capitalize()}!")
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı!")

else:
    # Sayfanın en üstünde kimin giriş yaptığını gösterebilirsin
    st.sidebar.write(f"👤 Giriş yapan: **{st.session_state.aktif_kullanici}**")
    # --- 5. ANA PANEL ---
    df = veri_yukle()
    
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            secilen_marka = st.selectbox("Marka Seçin:", df['Marka'].unique())
            secilen_ay = st.selectbox("Ay Seçin:", df['Ay'].unique())
        
        st.divider()
        # VERİ VE MARKA YÖNETİMİ
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
        
        # Üst Metrikler (Dinamik ve Okunabilir)
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_ay_df['Takipci'].sum()):,}")
        c2.metric("Toplam Etkileşim", f"{int(m_ay_df['Etkilesim'].sum()):,}")
        c3.metric("Seçilen Ay", secilen_ay)

        st.divider()
        
        # 1. SATIR: AYDAN AYA TRENDLER
        st.subheader("📈 Aylık Gelişim Trendleri")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            fig1 = px.area(m_df.groupby('Ay')['Takipci'].sum().reset_index(), x='Ay', y='Takipci', title="Takipçi Trendi", color_discrete_sequence=['#FF4B4B'])
            st.plotly_chart(fig1, use_container_width=True)
        with col_t2:
            fig2 = px.line(m_df.groupby('Ay')['Etkilesim'].sum().reset_index(), x='Ay', y='Etkilesim', title="Etkileşim Trendi", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        
        # 2. SATIR: YOUTUBE ÖZEL VE DAĞILIM
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
