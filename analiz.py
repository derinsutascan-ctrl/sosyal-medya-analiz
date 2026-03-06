import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Teknostore Admin Panel", layout="wide")

# Şık Siyah Tema ve Giriş Kutusu CSS
st.markdown("""
    <style>
    .stMetric { background-color: #111; border: 1px solid #333; padding: 15px; border-radius: 10px; }
    [data-testid="stSidebar"] { min-width: 300px; }
    .login-box { max-width: 400px; margin: auto; padding: 2rem; border: 1px solid #333; border-radius: 10px; background: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI SİSTEMİ ---
DB_FILE = 'marka_veritabanı_2026.csv'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        # Tertemiz bir başlangıç için boş şablon
        df = pd.DataFrame(columns=['Marka', 'Ay', 'Platform', 'Takipci', 'Erisim'])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

# --- 3. OTURUM YÖNETİMİ (SAYFA YENİLESE DE GİTMEZ) ---
if "oturum_durumu" not in st.session_state:
    st.session_state.oturum_durumu = False

# --- 4. GİRİŞ EKRANI (ORTALANMIŞ VE KÜÇÜK) ---
if not st.session_state.oturum_durumu:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.title("🔐 Panel Girişi")
        user = st.text_input("Kullanıcı Adı")
        pw = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if user == "admin" and pw == "teknostore123":
                st.session_state.oturum_durumu = True
                st.rerun()
            else:
                st.error("Hatalı bilgiler!")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 5. ANA PANEL ---
    df = veri_yukle()
    
    with st.sidebar:
        st.title("🚀 Yönetim Menüsü")
        
        # ANA SAYFA VE MARKA SEÇİMİ
        sayfa_modu = st.radio("Görünüm Seçin:", ["🏠 Genel Bakış (Tüm Markalar)", "📊 Marka Bazlı Detay"])
        
        if sayfa_modu == "📊 Marka Bazlı Detay":
            marka_listesi = df['Marka'].unique().tolist()
            if not marka_listesi:
                st.info("Henüz marka eklenmemiş.")
                secilen_marka = None
            else:
                secilen_marka = st.selectbox("Marka Seçin:", marka_listesi)
                secilen_ay = st.selectbox("Ay Seçin:", ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026"])
        
        st.divider()
        
        # VERİ YÖNETİMİ VE YENİ MARKA EKLEME
        st.subheader("🛠️ Veri & Marka Ekle")
        with st.expander("Yeni Kayıt / Güncelleme"):
            with st.form("veri_formu"):
                # Yeni marka ekleme veya mevcut seçme
                mevcut_markalar = ["--- Yeni Marka Ekle ---"] + df['Marka'].unique().tolist()
                f_marka_sec = st.selectbox("Marka Seçin", mevcut_markalar)
                f_yeni_marka = st.text_input("Yeni Marka Adı (Eğer yeniyse)")
                
                f_ay = st.selectbox("Dönem", ["Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026"])
                
                st.markdown("**Platform Verileri (Rakamları tam girin)**")
                ig_t = st.number_input("Instagram Takipçi", min_value=0, step=1, format="%d")
                ig_e = st.number_input("Instagram Erişim", min_value=0, step=1, format="%d")
                
                fb_t = st.number_input("Facebook Takipçi", min_value=0, step=1, format="%d")
                fb_e = st.number_input("Facebook Erişim", min_value=0, step=1, format="%d")
                
                yt_t = st.number_input("YouTube Takipçi", min_value=0, step=1, format="%d")
                yt_e = st.number_input("YouTube Erişim", min_value=0, step=1, format="%d")
                
                if st.form_submit_button("Verileri Kaydet"):
                    final_marka = f_yeni_marka if f_marka_sec == "--- Yeni Marka Ekle ---" else f_marka_sec
                    
                    if final_marka:
                        # Eskileri temizle
                        df = df[~((df['Marka'] == final_marka) & (df['Ay'] == f_ay))]
                        # Yeni satırları oluştur (Sadece 0'dan büyükse veya hepsini 0 olarak ekle)
                        yeni_data = [
                            {'Marka': final_marka, 'Ay': f_ay, 'Platform': 'Instagram', 'Takipci': ig_t, 'Erisim': ig_e},
                            {'Marka': final_marka, 'Ay': f_ay, 'Platform': 'Facebook', 'Takipci': fb_t, 'Erisim': fb_e},
                            {'Marka': final_marka, 'Ay': f_ay, 'Platform': 'YouTube', 'Takipci': yt_t, 'Erisim': yt_e}
                        ]
                        df = pd.concat([df, pd.DataFrame(yeni_data)], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)
                        st.success(f"{final_marka} kaydedildi!")
                        st.rerun()

        st.divider()
        if st.button("Güvenli Çıkış"):
            st.session_state.oturum_durumu = False
            st.rerun()

    # --- 6. GÖRÜNTÜLEME ALANI ---
    if sayfa_modu == "🏠 Genel Bakış (Tüm Markalar)":
        st.title("🏠 Tüm Markaların Genel Durumu")
        if not df.empty:
            # Tüm markaların toplam takipçi sayılarını kıyaslayan grafik
            ozet_df = df.groupby('Marka')['Takipci'].sum().reset_index()
            fig_genel = px.bar(ozet_df, x='Marka', y='Takipci', title="Toplam Marka Gücü (Takipçi)", template="plotly_dark")
            st.plotly_chart(fig_genel, use_container_width=True)
            st.write("Marka bazlı detayları görmek için sol menüden 'Marka Bazlı Detay'ı seçin.")
        else:
            st.warning("Henüz veri girilmemiş. Sol taraftaki 'Veri & Marka Ekle' alanından başlayın.")

    elif sayfa_modu == "📊 Marka Bazlı Detay" and 'secilen_marka' in locals() and secilen_marka:
        m_df = df[(df['Marka'] == secilen_marka) & (df['Ay'] == secilen_ay)]
        
        st.title(f"📊 {secilen_marka} - {secilen_ay} Analizi")
        
        if not m_df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Takipçi", f"{int(m_df['Takipci'].sum()):,}")
            c2.metric("Toplam Erişim", f"{int(m_df['Erisim'].sum()):,}")
            c3.metric("Platform Sayısı", len(m_df[m_df['Takipci'] > 0]))

            st.divider()

            col_l, col_r = st.columns([2, 1])
            with col_l:
                # Sadece veri olan platformları göster
                grafik_df = m_df[m_df['Takipci'] > 0]
                fig = px.bar(grafik_df, x='Platform', y='Takipci', color='Platform',
                             color_discrete_map={'Instagram':'#E1306C', 'Facebook':'#4267B2', 'YouTube':'#FF0000'},
                             template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                fig_p = px.pie(m_df, values='Erisim', names='Platform', hole=0.4, template="plotly_dark")
                st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info(f"{secilen_marka} için {secilen_ay} verisi henüz girilmemiş.")
