import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Teknostore Gelişmiş Analiz", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px; border-radius: 12px;
    }
    .login-container { display: flex; flex-direction: column; align-items: center; margin-top: 50px; }
    .login-box { width: 380px; padding: 30px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ SİSTEMİ (Yeni Sütunlar: Etkileşim ve YT İzlenme) ---
DB_FILE = 'marka_analiz_2026_v2.csv'

def veri_yukle():
    if not os.path.exists(DB_FILE):
        # Örnek başlangıç verileri (Trendi görebilmen için 3 aylık)
        data = []
        markalar = ['Teknostore', 'Aula', 'Nowgo']
        aylar = ['Ocak', 'Şubat', 'Mart']
        for m in markalar:
            for a in aylar:
                for p in ['Instagram', 'Facebook', 'YouTube']:
                    val = 1000 if a == 'Ocak' else (1200 if a == 'Şubat' else 1500)
                    data.append({
                        'Marka': m, 'Ay': a, 'Platform': p, 
                        'Takipci': val, 'Etkilesim': val/10, 'YT_Izlenme': val*5 if p == 'YouTube' else 0
                    })
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

# --- 3. OTURUM VE GİRİŞ ---
if "oturum" not in st.session_state: st.session_state.oturum = False

if not st.session_state.oturum:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        if os.path.exists("logo.png"): st.image("logo.png", width=350)
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            u = st.text_input("Kullanıcı")
            p = st.text_input("Şifre", type="password")
            if st.button("Giriş", use_container_width=True):
                if u == "admin" and p == "teknostore123":
                    st.session_state.oturum = True
                    st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
else:
    df = veri_yukle()
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        menu = st.radio("Bölüm Seçin", ["🏠 Genel Trendler", "📊 Marka Detay Analizi", "⚙️ Veri Yönetimi"])
        if st.button("Çıkış Yap"):
            st.session_state.oturum = False
            st.rerun()

    # --- 4. GENEL TRENDLER (TÜM MARKALAR) ---
    if menu == "🏠 Genel Trendler":
        st.title("🏠 Marka Performans Trendleri (2026)")
        
        # Takipçi Artış Grafiği (Çizgi)
        trend_df = df.groupby(['Ay', 'Marka'])['Takipci'].sum().reset_index()
        # Ayları sıralamak için
        ay_sirasi = {'Ocak':1, 'Şubat':2, 'Mart':3, 'Nisan':4, 'Mayıs':5}
        trend_df['Sira'] = trend_df['Ay'].map(ay_sirasi)
        trend_df = trend_df.sort_values('Sira')

        fig_line = px.line(trend_df, x='Ay', y='Takipci', color='Marka', markers=True,
                          title="Aylık Toplam Takipçi Değişimi", template="plotly_dark")
        st.plotly_chart(fig_line, use_container_width=True)
        

    # --- 5. MARKA DETAY ANALİZİ ---
    elif menu == "📊 Marka Detay Analizi":
        m_sec = st.selectbox("Marka Seçin", df['Marka'].unique())
        m_df = df[df['Marka'] == m_sec]
        
        st.title(f"📊 {m_sec} Analiz Raporu")
        
        tab1, tab2, tab3 = st.tabs(["📈 Takipçi & Etkileşim", "🎥 YouTube Özel", "🥧 Platform Dağılımı"])
        
        with tab1:
            col1, col2 = st.columns(2)
            # Takipçi Trendi
            fig1 = px.area(m_df.groupby('Ay')['Takipci'].sum().reset_index(), x='Ay', y='Takipci', 
                          title="Aylık Takipçi Trendi", color_discrete_sequence=['#00CC96'])
            col1.plotly_chart(fig1, use_container_width=True)
            
            # Etkileşim Trendi
            fig2 = px.line(m_df.groupby('Ay')['Etkilesim'].sum().reset_index(), x='Ay', y='Etkilesim', 
                          title="Aylık Etkileşim Oranları", markers=True)
            col2.plotly_chart(fig2, use_container_width=True)

        with tab2:
            st.subheader("🎥 YouTube Aylık İzlenme Performansı")
            yt_df = m_df[m_df['Platform'] == 'YouTube']
            if not yt_df.empty:
                fig_yt = px.bar(yt_df, x='Ay', y='YT_Izlenme', title="YouTube İzlenme Sayıları",
                               color='YT_Izlenme', color_continuous_scale='Reds')
                st.plotly_chart(fig_yt, use_container_width=True)
                
            else:
                st.warning("Bu markaya ait YouTube verisi bulunamadı.")

        with tab3:
            ay_filtre = st.selectbox("Dağılım İçin Ay Seçin", m_df['Ay'].unique())
            pie_df = m_df[m_df['Ay'] == ay_filtre]
            fig_pie = px.pie(pie_df, values='Takipci', names='Platform', hole=0.5, title=f"{ay_filtre} Platform Payı")
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- 6. VERİ YÖNETİMİ ---
    elif menu == "⚙️ Veri Yönetimi":
        st.title("⚙️ Veri Girişi ve Güncelleme")
        with st.form("yeni_veri"):
            c1, c2, c3 = st.columns(3)
            marka = c1.text_input("Marka Adı")
            ay = c2.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran"])
            platform = c3.selectbox("Platform", ["Instagram", "Facebook", "YouTube"])
            
            v1, v2, v3 = st.columns(3)
            takipci = v1.number_input("Takipçi Sayısı", min_value=0)
            etkilesim = v2.number_input("Etkileşim Sayısı", min_value=0)
            izlenme = v3.number_input("YT İzlenme (Sadece YouTube ise)", min_value=0)
            
            if st.form_submit_button("Veriyi Kaydet"):
                # Mevcut kaydı silip yenisini ekle (Update mantığı)
                df = df[~((df['Marka'] == marka) & (df['Ay'] == ay) & (df['Platform'] == platform))]
                yeni = {'Marka': marka, 'Ay': ay, 'Platform': platform, 
                        'Takipci': takipci, 'Etkilesim': etkilesim, 'YT_Izlenme': izlenme}
                df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("Veri başarıyla işlendi!")
                st.rerun()
