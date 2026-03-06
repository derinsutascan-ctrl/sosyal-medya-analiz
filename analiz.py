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

st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# CSS: Tasarımını Birebir Korur
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

# --- 2. VERİ VE KULLANICI SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026_final.csv'
USER_DB = 'kullanicilar.csv'
SESSION_FILE = 'active_session.txt' # Giriş bilgisini burada saklayacağız

def veri_yukle():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Platform', 'Takipci', 'Etkilesim', 'YT_Izlenme'])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

def kullanicilari_yukle():
    if not os.path.exists(USER_DB):
        df_u = pd.DataFrame([{"user": "admin", "pass": "teknostore123", "role": "Ana Kullanıcı"}])
        df_u.to_csv(USER_DB, index=False)
        return df_u
    return pd.read_csv(USER_DB)

# --- 3. OTURUM KONTROLÜ (GİRİŞİ HATIRLAYAN BÖLÜM) ---
df_kullanicilar = kullanicilari_yukle()
KULLANICILAR = dict(zip(df_kullanicilar['user'], df_kullanicilar['pass']))

# Sayfa yenilense de dosyadan oku
if os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, 'r') as f:
        saved_user = f.read().strip()
        if saved_user in KULLANICILAR:
            st.session_state.oturum_durumu = True
            st.session_state.aktif_kullanici = saved_user

if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False
if "aktif_kullanici" not in st.session_state:
    st.session_state.aktif_kullanici = ""

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=250)
    
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0;'>🔐 Yönetim Girişi</h3>", unsafe_allow_html=True)
        u = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınız...", key="l_u")
        p = st.text_input("Şifre", type="password", placeholder="Şifreniz...", key="l_p")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if u in KULLANICILAR and KULLANICILAR[u] == p:
                st.session_state.oturum_durumu = True
                st.session_state.aktif_kullanici = u
                # GİRİŞİ KAYDET: Sayfa yenilense de hatırlar
                with open(SESSION_FILE, 'w') as f:
                    f.write(u)
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL (SAYFA YENİLENSE DE BURADAN DEVAM EDER) ---
    df = veri_yukle()
    
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        st.info(f"👤 Kullanıcı: {st.session_state.aktif_kullanici}")

        # --- YENİ: KULLANICI EKLEME (Admin Paneli) ---
        if st.session_state.aktif_kullanici == "admin":
            st.divider()
            with st.expander("👤 Ekip Arkadaşı Yönetimi"):
                new_u = st.text_input("Yeni Kullanıcı", key="add_u")
                new_p = st.text_input("Şifre", type="password", key="add_p")
                if st.button("Tanımla"):
                    if new_u and new_p:
                        yeni_uye = pd.DataFrame([{"user": new_u, "pass": new_p, "role": "Üye"}])
                        df_kullanicilar = pd.concat([df_kullanicilar, yeni_uye], ignore_index=True)
                        df_kullanicilar.to_csv(USER_DB, index=False)
                        st.success("Eklendi!")
                        st.rerun()

        st.divider()
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            markalar = df['Marka'].unique().tolist()
            secilen_marka = st.selectbox("Marka Seçin:", markalar if markalar else ["Veri Yok"])
            aylar = df['Ay'].unique().tolist()
            secilen_ay = st.selectbox("Ay Seçin:", aylar if aylar else ["Veri Yok"])
        
        st.divider()
        with st.expander("🛠️ Veri Güncelle"):
            with st.form("admin_form"):
                f_secim = st.selectbox("Marka", ["--- Yeni ---"] + df['Marka'].unique().tolist())
                f_yeni_ad = st.text_input("Ad")
                f_ay = st.selectbox("Ay", ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026"])
                f_plat = st.selectbox("Platform", ["Instagram", "Facebook", "YouTube"])
                f_takipci = st.number_input("Takipçi", min_value=0)
                f_etkilesim = st.number_input("Etkileşim", min_value=0)
                f_izlenme = st.number_input("YT İzlenme", min_value=0)
                
                if st.form_submit_button("Kaydet"):
                    final_m = f_yeni_ad if f_secim == "--- Yeni ---" else f_secim
                    if final_m:
                        df = df[~((df['Marka'] == final_m) & (df['Ay'] == f_ay) & (df['Platform'] == f_plat))]
                        yeni = {'Marka': final_m, 'Ay': f_ay, 'Platform': f_plat, 'Takipci': f_takipci, 'Etkilesim': f_etkilesim, 'YT_Izlenme': f_izlenme}
                        df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.success("İşlendi!")
                        st.rerun()

        if st.button("Güvenli Çıkış (Oturumu Kapat)", use_container_width=True):
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. RAPORLAMA ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Tüm Markaların Genel Trendi")
        if not df.empty:
            trend_df = df.groupby(['Ay', 'Marka'])['Takipci'].sum().reset_index()
            fig_trend = px.line(trend_df, x='Ay', y='Takipci', color='Marka', markers=True)
            st.plotly_chart(fig_trend, use_container_width=True)
        
    else:
        st.title(f"📊 {secilen_marka} Performans Analizi")
        m_df = df[df['Marka'] == secilen_marka]
        m_ay_df = m_df[m_df['Ay'] == secilen_ay]
        
        if not m_ay_df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Takipçi", f"{int(m_ay_df['Takipci'].sum()):,}")
            c2.metric("Toplam Etkileşim", f"{int(m_ay_df['Etkilesim'].sum()):,}")
            c3.metric("Seçilen Ay", secilen_ay)

            st.divider()
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.plotly_chart(px.area(m_df.groupby('Ay')['Takipci'].sum().reset_index(), x='Ay', y='Takipci', title="Takipçi Trendi"), use_container_width=True)
            with col_t2:
                st.plotly_chart(px.line(m_df.groupby('Ay')['Etkilesim'].sum().reset_index(), x='Ay', y='Etkilesim', title="Etkileşim Trendi", markers=True), use_container_width=True)
        else:
            st.warning("Bu seçim için veri bulunamadı.")
