import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI (AYNI KALDI) ---
st.set_page_config(page_title="Teknostore Rapor Paneli", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .login-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; margin-top: 20px; }
    .login-box { max-width: 360px; width: 100%; padding: 25px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; }
    div[data-testid="stMetric"] { background-color: rgba(128, 128, 128, 0.08); border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 12px; }
    .plat-header { background: #f8f9fb; padding: 8px; border-radius: 8px; border-left: 5px solid #ff4b4b; margin: 15px 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ VE KULLANICI SİSTEMİ (GÜN SÜTUNU EKLENDİ) ---
DB_FILE = 'marka_veritabani_2026_final.csv'
USER_DB = 'kullanicilar.csv'
SESSION_FILE = 'active_session.txt'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        # Gun sütunu eklendi
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Gun', 'Platform', 'Takipci', 'Etkilesim', 'YT_Izlenme'])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

# --- 3. OTURUM KONTROLÜ (AYNI KALDI) ---
# ... (Kullanıcı yükleme ve login fonksiyonların burada yer alıyor) ...

# --- 5. ANA PANEL VE YENİLİKLER ---
if "oturum_durumu" in st.session_state and st.session_state.oturum_durumu:
    df = veri_yukle()
    AYLAR_LISTESI = ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026", "Haziran 2026", 
                     "Temmuz 2026", "Ağustos 2026", "Eylül 2026", "Ekim 2026", "Kasım 2026", "Aralık 2026"]

    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        st.title("🚀 Menü")
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            st.divider()
            secilen_marka = st.selectbox("Marka Seçin:", df['Marka'].unique() if not df.empty else ["Veri Yok"])
            secilen_ay = st.selectbox("Ay Seçin:", AYLAR_LISTESI)

        st.divider()
        with st.expander("🛠️ Yeni Marka / Günlük Veri Güncelle"):
            with st.form("admin_form"):
                f_secim = st.selectbox("Marka Seç", ["--- Yeni Marka Ekle ---"] + df['Marka'].unique().tolist())
                f_yeni_ad = st.text_input("Yeni Marka Adı (Eklenecekse)")
                f_ay = st.selectbox("Dönem", AYLAR_LISTESI)
                f_gun = st.number_input("Gün", min_value=1, max_value=31, step=1) # Yeni: Gün seçimi
                f_plat = st.selectbox("Platform", ["Instagram", "Facebook", "YouTube"])
                f_takipci = st.number_input("Takipçi Sayısı", min_value=0)
                f_etkilesim = st.number_input("Etkileşim Sayısı", min_value=0)
                f_izlenme = st.number_input("YT İzlenme (Sadece YouTube)", min_value=0)
                
                if st.form_submit_button("Sisteme Kaydet"):
                    final_m = f_yeni_ad if f_secim == "--- Yeni Marka Ekle ---" else f_secim
                    if final_m:
                        # Kayıt kontrolüne 'Gun' eklendi
                        df = df[~((df['Marka'] == final_m) & (df['Ay'] == f_ay) & (df['Gun'] == f_gun) & (df['Platform'] == f_plat))]
                        yeni = {'Marka': final_m, 'Ay': f_ay, 'Gun': f_gun, 'Platform': f_plat, 'Takipci': f_takipci, 'Etkilesim': f_etkilesim, 'YT_Izlenme': f_izlenme}
                        df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.success("Kaydedildi!")
                        st.rerun()

    # --- 6. RAPORLAMA VE GRAFİKLER ---
    if sayfa_modu == "📊 Marka Bazlı Detay":
        # Veriyi seçilen aya ve markaya göre filtrele, günlere göre sırala
        m_ay_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)].sort_values(by='Gun')
        
        st.title(f"📊 {secilen_marka} Performans Analizi ({secilen_ay})")
        
        # Üst Metrikler (AYNI KALDI)
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Takipçi", f"{int(m_ay_df['Takipci'].sum()):,}")
        c2.metric("Toplam Etkileşim", f"{int(m_ay_df['Etkilesim'].sum()):,}")
        c3.metric("Seçilen Ay", secilen_ay)

        st.divider()

        # 🎯 YENİLİK: HER PLATFORM İÇİN AYRI ÇİZGİ GRAFİKLERİ
        for plat in ["Instagram", "Facebook", "YouTube"]:
            st.markdown(f'<div class="plat-header">{plat} Günlük Detayları</div>', unsafe_allow_html=True)
            p_data = m_ay_df[m_ay_df['Platform'] == plat]
            
            if not p_data.empty:
                col_left, col_right = st.columns(2)
                with col_left:
                    # Bar yerine Çizgi grafiği eklendi, alt satır GÜN oldu
                    fig_t = px.line(p_data, x='Gun', y='Takipci', title=f"{plat} Günlük Takipçi", markers=True)
                    fig_t.update_xaxes(dtick=1)
                    st.plotly_chart(fig_t, use_container_width=True)
                with col_right:
                    fig_e = px.line(p_data, x='Gun', y='Etkilesim', title=f"{plat} Günlük Etkileşim", markers=True, color_discrete_sequence=['#FFD43B'])
                    fig_e.update_xaxes(dtick=1)
                    st.plotly_chart(fig_e, use_container_width=True)
            else:
                st.info(f"{plat} için {secilen_ay} ayında veri bulunamadı.")

        st.divider()

        # 🎯 YENİLİK: TÜMÜNÜN AYNI GRAFİKTE OLDUĞU ÇİZGİ GRAFİĞİ
        st.subheader("⚖️ Tüm Platformların Günlük Takipçi Kıyaslaması")
        fig_genel = px.line(m_ay_df, x='Gun', y='Takipci', color='Platform', markers=True)
        fig_genel.update_xaxes(dtick=1)
        st.plotly_chart(fig_genel, use_container_width=True)

        st.divider()

        # ALT BÖLÜM: YOUTUBE VE PASTA GRAFİĞİ (AYNI KALDI)
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            st.subheader("🎥 YouTube İzlenme Analizi")
            yt_data = m_ay_df[m_ay_df['Platform'] == 'YouTube']
            if not yt_data.empty:
                fig_yt = px.bar(yt_data, x='Gun', y='YT_Izlenme', color='YT_Izlenme', color_continuous_scale='Reds')
                st.plotly_chart(fig_yt, use_container_width=True)
        
        with col_b2:
            st.subheader("🥧 Platform Dağılımı")
            fig_pie = px.pie(m_ay_df, values='Takipci', names='Platform', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
