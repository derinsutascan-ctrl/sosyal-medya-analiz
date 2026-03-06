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

# Tarayıcıların (Android/Windows) otomatik çeviri yapıp linki bozmasını engeller
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# ÖZEL CSS: Giriş kutusunu daraltır ve her cihazda tam ortaya yerleştirir
st.markdown("""
    <style>
    /* Giriş sayfası için dikey ve yatay merkezleme */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
    }
    
    /* FORM KUTUSU: Maksimum 360px genişlik (Minimum ve şık boyut) */
    .login-box {
        max-width: 360px; 
        width: 100%;
        padding: 30px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 15px;
        background-color: rgba(255, 255, 255, 0.02);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Logo altındaki boşluk */
    .logo-spacing {
        margin-bottom: 25px;
        text-align: center;
    }

    /* Metrik kartları tasarımı (İç sayfadaki veriler için) */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KULLANICI YETKİLERİ (Buraya dilediğin kadar kişi ekleyebilirsin) ---
KULLANICILAR = {
    "admin": "teknostore123",
    "pazarlama": "satis2026",
    "analiz": "rapor456"
}

# --- 3. VERİ TABANI SİSTEMİ ---
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

# --- 4. OTURUM YÖNETİMİ ---
if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False
if "aktif_kullanici" not in st.session_state:
    st.session_state.aktif_kullanici = ""

# --- 5. GİRİŞ EKRANI KONTROLÜ ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Logo Bölümü
    st.markdown('<div class="logo-spacing">', unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=300)
    else:
        st.title("TEKNOSTORE")
    st.markdown('</div>', unsafe_allow_html=True)

    # Giriş Kutusu (Küçültülmüş kolon yapısı ile)
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom:20px;'>🔐 Yönetim Girişi</h3>", unsafe_allow_html=True)
        
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
    # --- 6. ANA ANALİZ PANELİ (Giriş Başarılıysa Burası Çalışır) ---
    df = veri_yukle()
    
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        st.info(f"👤 Kullanıcı: {st.session_state.aktif_kullanici}")
        
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

    # --- 7. RAPORLAMA VE GRAFİKLER ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Tüm Markaların Genel Karşılaştırması")
        trend_df = df.groupby(['Ay', 'Marka'])['Takipci'].sum().reset_index()
        fig_trend = px.line(trend_df, x='Ay', y='Takipci', color='Marka', markers=True, title="Aylık Toplam Takipçi Gelişimi")
        st.plotly_chart(fig_trend, use_container_width=True)

    else:
        m_df = df[df['Marka'] == secilen_marka]
        m_ay_df = m_df[m_df['Ay'] == secilen_ay]
        
        st.title(f"📊 {secilen_marka} - {secilen_ay} Analiz Raporu")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_ay_df['Takipci'].sum()):,}")
        c2.metric("Toplam Etkileşim", f"{int(m_ay_df['Etkilesim'].sum()):,}")
        c3.metric("Seçilen Dönem", secilen_ay)

        st.divider()
        st.subheader("📈 Aylık Performans Değişimi (Trend)")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            fig1 = px.area(m_df.groupby('Ay')['Takipci'].sum().reset_index(), x='Ay', y='Takipci', title="Takipçi Sayısı Trendi (Aylık)", color_discrete_sequence=['#00CC96'])
            st.plotly_chart(fig1, use_container_width=True)
        with col_t2:
            fig2 = px.line(m_df.groupby('Ay')['Etkilesim'].sum().reset_index(), x='Ay', y='Etkilesim', title="Etkileşim Sayısı Trendi (Aylık)", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            st.subheader("🎥 YouTube İzlenme Analizi")
            yt_data = m_df[m_df['Platform'] == 'YouTube']
            if not yt_data.empty:
                fig_yt = px.bar(yt_data, x='Ay', y='YT_Izlenme', title="Aylık YouTube İzlenme Sayıları", color='YT_Izlenme', color_continuous_scale='Reds')
                st.plotly_chart(fig_yt, use_container_width=True)
        with col_b2:
            st.subheader("🥧 Platform Dağılımı")
            fig_pie = px.pie(m_ay_df, values='Takipci', names='Platform', hole=0.4, title=f"{secilen_ay} Dağılım")
            st.plotly_chart(fig_pie, use_container_width=True)
