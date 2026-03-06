import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .login-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; margin-top: 20px; }
    .login-box { max-width: 360px; width: 100%; padding: 25px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; }
    div[data-testid="stMetric"] { background-color: rgba(128, 128, 128, 0.08); border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 12px; }
    .plat-card { background: #f8f9fb; padding: 10px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin: 10px 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME ---
DB_FILE = 'marka_veritabani_2026_final.csv'
USER_DB = 'kullanicilar.csv'
SESSION_FILE = 'active_session.txt'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Hafta', 'Platform', 'Takipci', 'Etkilesim', 'YT_Izlenme'])
        df.to_csv(DB_FILE, index=False)
        return df
    df = pd.read_csv(DB_FILE)
    if 'Hafta' not in df.columns: df['Hafta'] = "1. Hafta"
    return df

# --- 3. OTURUM KONTROLÜ (Aynen Korundu) ---
def kullanicilari_yukle():
    if not os.path.exists(USER_DB):
        df_u = pd.DataFrame([{"user": "admin", "pass": "teknostore123", "role": "Ana Kullanıcı"}])
        df_u.to_csv(USER_DB, index=False)
        return df_u
    return pd.read_csv(USER_DB)

if "oturum_durumu" not in st.session_state: st.session_state.oturum_durumu = False
df_kullanicilar = kullanicilari_yukle()
KULLANICILAR = dict(zip(df_kullanicilar['user'], df_kullanicilar['pass']))

if not st.session_state.oturum_durumu and os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, 'r') as f:
        saved_user = f.read().strip()
        if saved_user in KULLANICILAR:
            st.session_state.oturum_durumu = True
            st.session_state.aktif_kullanici = saved_user

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0;'>🔐 Yönetim Girişi</h3>", unsafe_allow_html=True)
        u = st.text_input("Kullanıcı Adı", key="l_u")
        p = st.text_input("Şifre", type="password", key="l_p")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if u in KULLANICILAR and KULLANICILAR[u] == p:
                st.session_state.oturum_durumu = True
                st.session_state.aktif_kullanici = u
                with open(SESSION_FILE, 'w') as f: f.write(u)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL ---
    df = veri_yukle()
    AYLAR_LISTESI = ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026", "Haziran 2026"]
    HAFTALAR = ["1. Hafta", "2. Hafta", "3. Hafta", "4. Hafta"]

    with st.sidebar:
        st.title("🚀 Menü")
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            marka_listesi = sorted(df['Marka'].unique().tolist()) if not df.empty else ["Veri Yok"]
            secilen_marka = st.selectbox("Marka Seçin:", marka_listesi)
            secilen_ay = st.selectbox("Ay Seçin:", AYLAR_LISTESI)
        
        st.divider()
        with st.expander("🛠️ Veri Ekle/Güncelle"):
            with st.form("admin_form"):
                f_secim = st.selectbox("Marka", ["--- Yeni ---"] + sorted(df['Marka'].unique().tolist()))
                f_yeni_ad = st.text_input("Yeni Marka Adı")
                f_ay = st.selectbox("Dönem", AYLAR_LISTESI)
                f_hafta = st.selectbox("Hafta", HAFTALAR)
                f_plat = st.selectbox("Platform", ["Instagram", "Facebook", "YouTube"])
                f_takipci = st.number_input("Takipçi", min_value=0, max_value=100000000)
                f_etkilesim = st.number_input("Etkileşim", min_value=0, max_value=100000000)
                f_izlenme = st.number_input("YT İzlenme", min_value=0, max_value=100000000)
                if st.form_submit_button("Kaydet"):
                    final_m = f_yeni_ad if f_secim == "--- Yeni ---" else f_secim
                    if final_m:
                        df = df[~((df['Marka'] == final_m) & (df['Ay'] == f_ay) & (df['Hafta'] == f_hafta) & (df['Platform'] == f_plat))]
                        yeni = {'Marka': final_m, 'Ay': f_ay, 'Hafta': f_hafta, 'Platform': f_plat, 'Takipci': f_takipci, 'Etkilesim': f_etkilesim, 'YT_Izlenme': f_izlenme}
                        df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()

        if st.button("Güvenli Çıkış", use_container_width=True):
            if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. GRAFİKLER (İSTEDİĞİNİZ TEKİL GÖRÜNÜM) ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Tüm Markalar Haftalık Özet")
        df['Zaman'] = df['Ay'] + " " + df['Hafta']
        st.plotly_chart(px.line(df.groupby(['Zaman', 'Marka'])['Takipci'].sum().reset_index(), x='Zaman', y='Takipci', color='Marka', markers=True), use_container_width=True)
        
    else:
        m_ay_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)].sort_values(by='Hafta')
        
        st.title(f"📊 {secilen_marka} - {secilen_ay} Haftalık Analiz")
        
        # Üst Metrikler
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_ay_df['Takipci'].sum()):,}")
        c2.metric("Toplam Etkileşim", f"{int(m_ay_df['Etkilesim'].sum()):,}")
        c3.metric("Seçilen Ay", secilen_ay)

        st.divider()
        # İSTEDİĞİNİZ YER: TÜM PLATFORMLAR TEK GRAFİKTE
        st.subheader("📈 Haftalık Platform Karşılaştırması (Hepsi Bir Arada)")
        
        col_all1, col_all2 = st.columns(2)
        
        with col_all1:
            # Tüm platformların takipçileri tek grafikte yan yana çubuklar
            fig_all_t = px.bar(m_ay_df, x='Hafta', y='Takipci', color='Platform', barmode='group', 
                              title="Haftalık Takipçi Dağılımı (Instagram/FB/YT)", text_auto='.2s')
            st.plotly_chart(fig_all_t, use_container_width=True)
            
        with col_all2:
            # Tüm platformların etkileşimleri tek grafikte çizgiler
            fig_all_e = px.line(m_ay_df, x='Hafta', y='Etkilesim', color='Platform', markers=True,
                               title="Haftalık Etkileşim Trendi (Tüm Platformlar)")
            st.plotly_chart(fig_all_e, use_container_width=True)

        st.divider()
        # YouTube İzlenme ve Pasta Dağılımı
        col_low1, col_low2 = st.columns([2, 1])
        with col_low1:
            st.subheader("🎥 YouTube Haftalık İzlenme")
            yt_data = m_ay_df[m_ay_df['Platform'] == 'YouTube']
            if not yt_data.empty:
                st.plotly_chart(px.bar(yt_data, x='Hafta', y='YT_Izlenme', color='Hafta', title="Haftalık YouTube İzlenme Performansı"), use_container_width=True)
            else: st.info("YouTube verisi girilmemiş.")
        
        with col_low2:
            st.subheader("🥧 Ay Sonu Takipçi Payı")
            st.plotly_chart(px.pie(m_ay_df, values='Takipci', names='Platform', hole=0.4), use_container_width=True)
