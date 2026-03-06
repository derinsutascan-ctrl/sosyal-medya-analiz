import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# CSS: Tasarımını Birebir Korur
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .login-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; margin-top: 20px; }
    .login-box { max-width: 360px; width: 100%; padding: 25px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; }
    div[data-testid="stMetric"] { background-color: rgba(128, 128, 128, 0.08); border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 12px; }
    .plat-card { background: #f8f9fb; padding: 10px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin: 10px 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ VE KULLANICI SİSTEMİ ---
DB_FILE = 'marka_veritabani_2026_final.csv'
USER_DB = 'kullanicilar.csv'
SESSION_FILE = 'active_session.txt'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Platform', 'Takipci', 'Etkilesim', 'YT_Izlenme', 'Gun'])
        df.to_csv(DB_FILE, index=False)
        return df
    df = pd.read_csv(DB_FILE)
    if 'Gun' not in df.columns:
        df['Gun'] = 1
    return df

def kullanicilari_yukle():
    if not os.path.exists(USER_DB):
        df_u = pd.DataFrame([{"user": "admin", "pass": "teknostore123", "role": "Ana Kullanıcı"}])
        df_u.to_csv(USER_DB, index=False)
        return df_u
    return pd.read_csv(USER_DB)

# --- 3. OTURUM KONTROLÜ ---
if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False

df_kullanicilar = kullanicilari_yukle()
KULLANICILAR = dict(zip(df_kullanicilar['user'], df_kullanicilar['pass']))

if not st.session_state.oturum_durumu:
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            saved_user = f.read().strip()
            if saved_user in KULLANICILAR:
                st.session_state.oturum_durumu = True
                st.session_state.aktif_kullanici = saved_user

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.oturum_durumu:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    if os.path.exists("logo.png"): st.image("logo.png", width=250)
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
            else: st.error("Hatalı giriş!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL ---
    df = veri_yukle()
    AYLAR_LISTESI = ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026", "Haziran 2026", 
                     "Temmuz 2026", "Ağustos 2026", "Eylül 2026", "Ekim 2026", "Kasım 2026", "Aralık 2026"]

    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        st.info(f"👤 Kullanıcı: {st.session_state.aktif_kullanici}")

        if st.session_state.aktif_kullanici == "admin":
            st.divider()
            with st.expander("👤 Ekip Arkadaşı Yönetimi"):
                new_u = st.text_input("Kullanıcı", key="add_u")
                new_p = st.text_input("Şifre", type="password", key="add_p")
                if st.button("Tanımla"):
                    if new_u and new_p:
                        yeni_uye = pd.DataFrame([{"user": new_u, "pass": new_p, "role": "Ekip Üyesi"}])
                        df_kullanicilar = pd.concat([df_kullanicilar, yeni_uye], ignore_index=True)
                        df_kullanicilar.to_csv(USER_DB, index=False)
                        st.success("Eklendi!")
                        st.rerun()

        st.divider()
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            marka_listesi = df['Marka'].unique().tolist() if not df.empty else ["Veri Yok"]
            secilen_marka = st.selectbox("Marka Seçin:", marka_listesi)
            secilen_ay = st.selectbox("Ay Seçin:", AYLAR_LISTESI)
        
        st.divider()
        with st.expander("🛠️ Yeni Marka / Veri Güncelle"):
            with st.form("admin_form"):
                f_secim = st.selectbox("Marka Seç", ["--- Yeni ---"] + df['Marka'].unique().tolist())
                f_yeni_ad = st.text_input("Yeni Marka Adı")
                f_ay = st.selectbox("Dönem", AYLAR_LISTESI)
                f_plat = st.selectbox("Platform", ["Instagram", "Facebook", "YouTube"])
                
                # 100 BİN ÜZERİ DEĞERLER İÇİN GÜNCELLENDİ
                f_takipci = st.number_input("Takipçi", min_value=0, max_value=10000000, step=100)
                f_etkilesim = st.number_input("Etkileşim", min_value=0, max_value=10000000, step=100)
                f_izlenme = st.number_input("YT İzlenme", min_value=0, max_value=10000000, step=100)
                
                if st.form_submit_button("Sisteme Kaydet"):
                    final_m = f_yeni_ad if f_secim == "--- Yeni ---" else f_secim
                    if final_m:
                        df = df[~((df['Marka'] == final_m) & (df['Ay'] == f_ay) & (df['Platform'] == f_plat))]
                        yeni = {'Marka': final_m, 'Ay': f_ay, 'Platform': f_plat, 'Takipci': f_takipci, 'Etkilesim': f_etkilesim, 'YT_Izlenme': f_izlenme, 'Gun': 1}
                        df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.success("Kaydedildi!")
                        st.rerun()

        if st.button("Güvenli Çıkış", use_container_width=True):
            if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. RAPORLAMA VE GRAFİKLER ---
    if sayfa_modu == "🏠 Genel Bakış":
        st.title("🏠 Tüm Markaların Genel Trendi")
        if not df.empty:
            col_genel1, col_genel2 = st.columns(2)
            with col_genel1:
                st.subheader("👥 Takipçi Trendi")
                trend_df = df.groupby(['Ay', 'Marka'])['Takipci'].sum().reset_index()
                st.plotly_chart(px.line(trend_df, x='Ay', y='Takipci', color='Marka', markers=True), use_container_width=True)
            with col_genel2:
                st.subheader("🔥 Etkileşim Trendi")
                etk_trend_df = df.groupby(['Ay', 'Marka'])['Etkilesim'].sum().reset_index()
                st.plotly_chart(px.line(etk_trend_df, x='Ay', y='Etkilesim', color='Marka', markers=True), use_container_width=True)
        
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
        st.subheader("📱 Platformlara Göre Özel Analiz")
        for plat in ["Instagram", "Facebook", "YouTube"]:
            st.markdown(f'<div class="plat-card">{plat.upper()} Analizi</div>', unsafe_allow_html=True)
            p_data = m_ay_df[m_ay_df['Platform'] == plat]
            pc1, pc2 = st.columns(2)
            with pc1:
                st.plotly_chart(px.bar(p_data, x='Platform', y='Takipci', title=f"{plat} Takipçi", color_discrete_sequence=['#4B8BBE']), use_container_width=True)
            with pc2:
                st.plotly_chart(px.bar(p_data, x='Platform', y='Etkilesim', title=f"{plat} Etkileşim", color_discrete_sequence=['#FFD43B']), use_container_width=True)

        st.divider()
        st.subheader("🌐 Platformlar Arası Kıyaslama (Tek Grafik)")
        col_comp1, col_comp2 = st.columns(2)
        with col_comp1:
            st.plotly_chart(px.bar(m_ay_df, x='Platform', y='Takipci', color='Platform', title=f"{secilen_ay} Tüm Takipçiler", text_auto='.2s'), use_container_width=True)
        with col_comp2:
            st.plotly_chart(px.bar(m_ay_df, x='Platform', y='Etkilesim', color='Platform', title=f"{secilen_ay} Tüm Etkileşimler", text_auto='.2s'), use_container_width=True)

        st.divider()
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            st.subheader("🎥 YouTube İzlenme Analizi")
            yt_data = m_df[m_df['Platform'] == 'YouTube']
            if not yt_data.empty:
                st.plotly_chart(px.bar(yt_data, x='Ay', y='YT_Izlenme', title="Aylık YouTube İzlenme Sayıları", color='YT_Izlenme', color_continuous_scale='Reds'), use_container_width=True)
            else: st.info("YouTube verisi bulunamadı.")
        
        with col_b2:
            st.subheader("🥧 Platform Dağılımı")
            st.plotly_chart(px.pie(m_ay_df, values='Takipci', names='Platform', hole=0.4, title=f"{secilen_ay} Takipçi Payı"), use_container_width=True)
