import streamlit as st
import json
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ekip Takip", page_icon="🕌", layout="centered")

# --- CSS AYARLARI ---
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    .stButton>button { width: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS BAĞLANTISI ---
SHEET_ADI = "EkipTakipVeri" # Google Sheets'teki dosya adınız

def get_google_sheet():
    """Google Sheets bağlantısını kurar."""
    # Streamlit Secrets'tan bilgileri alıyoruz
    creds_dict = st.secrets["gcp_service_account"]
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open(SHEET_ADI).sheet1
        return sheet
    except Exception as e:
        st.error(f"Google Sheet bulunamadı! Lütfen dosya adının '{SHEET_ADI}' olduğundan ve servis hesabıyla paylaşıldığından emin olun.")
        st.stop()

def veri_yukle():
    """Veriyi Google Sheets A1 hücresinden çeker."""
    try:
        sheet = get_google_sheet()
        veri_raw = sheet.acell('A1').value
        if veri_raw:
            return json.loads(veri_raw)
        else:
            return {"gunluk_durum": {}, "cezalar": {}, "notlar": []}
    except Exception as e:
        # Eğer okuma hatası olursa boş dön
        return {"gunluk_durum": {}, "cezalar": {}, "notlar": []}

def veri_kaydet(veri):
    """Veriyi Google Sheets A1 hücresine yazar."""
    try:
        sheet = get_google_sheet()
        veri_str = json.dumps(veri, ensure_ascii=False)
        sheet.update_acell('A1', veri_str)
    except Exception as e:
        st.error(f"Kayıt hatası: {e}")

# --- SABİTLER ---
ekip = ["Ferhat", "Emre", "Selim", "Mustafa", "Veysel", "Furkan abi", "Osman"]
nobet_gunleri = {
    6: "Ferhat", 0: "Emre", 1: "Selim", 2: "Mustafa", 3: "Veysel", 4: "Furkan abi", 5: "Osman"
}
SIFRELER = {
    "Ferhat": "1453", "Emre": "2277", "Selim": "2007", "Mustafa": "4444",
    "Veysel": "7955", "Furkan abi": "1999", "Osman": "7070"
}
YETKILI_KISILER = ["Furkan abi", "Selim"]

temizlik_programi = [
    {"Hafta": "1. Hafta", "Banyo": "Ferhat", "Tuvalet": "Selim", "Mutfak": "Emre, Osman", "Salon": "Veysel", "İzinli": "Mustafa"},
    {"Hafta": "2. Hafta", "Banyo": "Mustafa", "Tuvalet": "Ferhat", "Mutfak": "Selim, Veysel", "Salon": "Emre", "İzinli": "Osman"},
    {"Hafta": "3. Hafta", "Banyo": "Osman", "Tuvalet": "Mustafa", "Mutfak": "Ferhat, Emre", "Salon": "Selim", "İzinli": "Veysel"},
    {"Hafta": "4. Hafta", "Banyo": "Veysel", "Tuvalet": "Osman", "Mutfak": "Mustafa, Selim", "Salon": "Ferhat", "İzinli": "Emre"},
    {"Hafta": "5. Hafta", "Banyo": "Emre", "Tuvalet": "Veysel", "Mutfak": "Osman, Ferhat", "Salon": "Mustafa", "İzinli": "Selim"},
    {"Hafta": "6. Hafta", "Banyo": "Selim", "Tuvalet": "Emre", "Mutfak": "Veysel, Mustafa", "Salon": "Osman", "İzinli": "Ferhat"}
]

# --- VERİ YÜKLEME ---
if "veri_cache" not in st.session_state:
    st.session_state["veri_cache"] = veri_yukle()
veri = st.session_state["veri_cache"]

# --- SAAT VE TARİH ---
tr_zamani = datetime.datetime.now() + datetime.timedelta(hours=3)
if tr_zamani.hour < 3 or (tr_zamani.hour == 3 and tr_zamani.minute < 30):
    gorev_tarihi = tr_zamani.date() - datetime.timedelta(days=1)
else:
    gorev_tarihi = tr_zamani.date()
bugun_str = str(gorev_tarihi)

# Veri Başlatma Kontrolleri
if "gunluk_durum" not in veri: veri["gunluk_durum"] = {}
if "cezalar" not in veri: veri["cezalar"] = {}
if "notlar" not in veri: veri["notlar"] = []

if bugun_str not in veri["gunluk_durum"]:
    veri["gunluk_durum"][bugun_str] = {kisi: {"risale": False, "yasin": False, "teravih": False} for kisi in ekip}
    # İlk açılışta hemen kaydet ki bulutta da bu günün kaydı oluşsun
    veri_kaydet(veri)

# Eski verileri temizleme (30 günden eski)
otuz_gun_once = str(datetime.date.today() - datetime.timedelta(days=30))
degisiklik_var = False
for eski_tarih in list(veri["gunluk_durum"].keys()):
    if eski_tarih < otuz_gun_once: 
        del veri["gunluk_durum"][eski_tarih]
        degisiklik_var = True
if degisiklik_var: veri_kaydet(veri)

# --- LOGIN SİSTEMİ ---
if "giris_yapan" not in st.session_state:
    params = st.query_params
    if "kullanici" in params and params["kullanici"] in ekip:
        st.session_state["giris_yapan"] = params["kullanici"]
    else:
        st.session_state["giris_yapan"] = None

if st.session_state["giris_yapan"] is None:
    st.markdown("<h1 style='text-align: center;'>🕌 Ekip Takip</h1>", unsafe_allow_html=True)
    st.write("")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        with st.form("giris_formu"):
            st.info("Giriş Yap")
            secilen_kisi = st.selectbox("İsim", ["Seçiniz..."] + ekip)
            girilen_sifre = st.text_input("Şifre", type="password")
            beni_hatirla = st.checkbox("Beni Hatırla")
            if st.form_submit_button("Giriş", use_container_width=True):
                if secilen_kisi != "Seçiniz..." and SIFRELER[secilen_kisi] == girilen_sifre:
                    st.session_state["giris_yapan"] = secilen_kisi
                    if beni_hatirla: st.query_params["kullanici"] = secilen_kisi
                    st.rerun()
                else:
                    st.error("Hatalı şifre!")
    st.stop()

aktif_kullanici = st.session_state["giris_yapan"]

# --- ARAYÜZ ---
col_header, col_logout = st.columns([7, 3])
with col_header:
    st.markdown(f"### 👋 Hoş geldin, {aktif_kullanici}")
with col_logout:
    if st.button("Çıkış Yap", key="logout_btn"):
        st.session_state["giris_yapan"] = None
        st.query_params.clear()
        st.rerun()

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🛡️ Nöbet", "📚 Görev", "⚖️ Ceza", "📊 İstatistik", "🧹 Temizlik", "📝 Notlar", "💾 Yedekle"])

with tab1: # NÖBET
    if tr_zamani.hour >= 23:
        nobet_icin_tarih = tr_zamani + datetime.timedelta(days=1)
        baslik_ek = "(Yarının Nöbetçisi - 23:00'den Sonra)"
    else:
        nobet_icin_tarih = tr_zamani
        baslik_ek = ""
    gunun_nobetcisi = nobet_gunleri[nobet_icin_tarih.weekday()]
    st.markdown(f"""
    <div style="background-color:#d4edda;padding:20px;border-radius:10px;text-align:center;border:2px solid #c3e6cb;">
        <h3 style="color:#155724;margin:0;">Nöbetçi {baslik_ek}</h3>
        <h1 style="color:#155724;font-size:40px;">{gunun_nobetcisi.upper()}</h1>
        <p style="color:#155724;margin:0;">{nobet_icin_tarih.strftime('%d.%m.%Y')}</p>
    </div>
    """, unsafe_allow_html=True)

with tab2: # GÖREVLER
    st.header(f"Görevler ({bugun_str})")
    for kisi in ekip:
        with st.container():
            st.markdown(f"**👤 {kisi}**")
            kutu_kilitli_mi = (kisi != aktif_kullanici)
            c1, c2, c3 = st.columns(3)
            g_verisi = veri["gunluk_durum"][bugun_str][kisi]
            
            with c1: r = st.checkbox("📖 Risale", value=g_verisi.get("risale", False), key=f"r_{kisi}", disabled=kutu_kilitli_mi)
            with c2: y = st.checkbox("📿 Yasin", value=g_verisi.get("yasin", False), key=f"y_{kisi}", disabled=kutu_kilitli_mi)
            with c3: t = st.checkbox("🕌 Teravih", value=g_verisi.get("teravih", False), key=f"t_{kisi}", disabled=kutu_kilitli_mi)

            if (r != g_verisi.get("risale")) or (y != g_verisi.get("yasin")) or (t != g_verisi.get("teravih")):
                veri["gunluk_durum"][bugun_str][kisi] = {"risale": r, "yasin": y, "teravih": t}
                veri_kaydet(veri)
                st.toast("Kaydedildi!")

with tab3: # CEZA
    st.subheader("Aktif Cezalar")
    aktif_ceza_var = False
    for kisi, ceza_listesi in veri.get("cezalar", {}).items():
        for i, ceza in enumerate(ceza_listesi):
            if not ceza.get("tamamlandi", False):
                aktif_ceza_var = True
                c1, c2 = st.columns([8, 3])
                with c1: st.error(f"**{kisi}:** {ceza['neden']}")
                with c2:
                    if aktif_kullanici == kisi or aktif_kullanici in YETKILI_KISILER:
                        if st.button("Tamamla", key=f"ct_{kisi}_{i}"):
                            ceza["tamamlandi"] = True
                            veri_kaydet(veri)
                            st.rerun()
    if not aktif_ceza_var: st.success("Herkes temiz!")

    if aktif_kullanici in YETKILI_KISILER:
        st.divider()
        with st.form("ceza_form"):
            col_kime, col_neden = st.columns([1, 2])
            kime = col_kime.selectbox("Kime?", ekip)
            neden = col_neden.text_input("Neden?")
            if st.form_submit_button("Ceza Yaz"):
                if neden:
                    if kime not in veri["cezalar"]: veri["cezalar"][kime] = []
                    veri["cezalar"][kime].append({"neden": neden, "tarih": bugun_str, "tamamlandi": False})
                    veri_kaydet(veri)
                    st.success("Yazıldı!")
                    st.rerun()

with tab4: # İSTATİSTİK
    st.subheader("📊 30 Günlük Özet")
    if aktif_kullanici in YETKILI_KISILER:
        toplam_gun_sayisi = len(veri["gunluk_durum"])
        
        # Bugün henüz kimse işlem yapmadıysa, bugünü istatistiğe dahil etme
        bugun_bos_mu = True
        if bugun_str in veri["gunluk_durum"]:
            for k in ekip:
                d = veri["gunluk_durum"][bugun_str][k]
                if d["risale"] or d["yasin"] or d["teravih"]:
                    bugun_bos_mu = False
                    break
        
        if bugun_bos_mu and toplam_gun_sayisi > 0:
            gosterilecek_gun_sayisi = toplam_gun_sayisi - 1
        else:
            gosterilecek_gun_sayisi = toplam_gun_sayisi
            
        if gosterilecek_gun_sayisi == 0: gosterilecek_gun_sayisi = 1

        st.info(f"Hesaplanan Gün Sayısı: **{gosterilecek_gun_sayisi}**")

        for kisi in ekip:
            r_say, y_say, t_say = 0, 0, 0
            for tarih, gun_verisi in veri["gunluk_durum"].items():
                if tarih == bugun_str and bugun_bos_mu:
                    continue
                d = gun_verisi.get(kisi, {})
                if d.get("risale"): r_say += 1
                if d.get("yasin"): y_say += 1
                if d.get("teravih"): t_say += 1
            
            with st.expander(f"👤 {kisi} - Detaylar"):
                m1, m2, m3 = st.columns(3)
                # İstediğiniz gibi kesirli formatta (örn: 3/4) gösterilir
                m1.metric("Risale", f"{r_say}/{gosterilecek_gun_sayisi}", f"{(gosterilecek_gun_sayisi-r_say) * -1} Eksik")
                m2.metric("Yasin", f"{y_say}/{gosterilecek_gun_sayisi}", f"{(gosterilecek_gun_sayisi-y_say) * -1} Eksik")
                m3.metric("Teravih", f"{t_say}/{gosterilecek_gun_sayisi}", f"{(gosterilecek_gun_sayisi-t_say) * -1} Eksik")

        st.divider()
        st.warning("⚠️ Tehlikeli Bölge")
        with st.expander("Verileri Sıfırla (Dikkat!)"):
            st.error("Bu işlem geri alınamaz!")
            if st.button("Evet, Her Şeyi Sil ve Sıfırla", type="primary"):
                veri["gunluk_durum"] = {}
                veri["cezalar"] = {}
                veri["notlar"] = []
                veri_kaydet(veri)
                st.success("Sıfırlandı!")
                st.rerun()
    else:
        st.warning("Yetkili değilsiniz.")

with tab5: # TEMİZLİK
    yh = tr_zamani.isocalendar()[1]
    ap = temizlik_programi[yh % 6]
    st.info(f"📍 **Şu anki Hafta: {ap['Hafta']}**")
    c1, c2 = st.columns(2)
    c1.markdown(f"**🚿 Banyo:** {ap['Banyo']}")
    c1.markdown(f"**🚽 Tuvalet:** {ap['Tuvalet']}")
    c2.markdown(f"**🍽️ Mutfak:** {ap['Mutfak']}")
    c2.markdown(f"**🛋️ Salon:** {ap['Salon']}")
    st.error(f"😴 **İzinli:** {ap['İzinli']}")
    st.dataframe(pd.DataFrame(temizlik_programi), hide_index=True, use_container_width=True)

with tab6: # NOTLAR
    st.header("Ortak Notlar")
    for i, n in enumerate(veri.get("notlar", [])):
        c1, c2 = st.columns([8, 1])
        with c1: st.info(f"**{n['kim']}:** {n['metin']}")
        with c2:
            if n['kim'] == aktif_kullanici and st.button("🗑️", key=f"del_note_{i}"):
                veri["notlar"].pop(i)
                veri_kaydet(veri)
                st.rerun()
    
    with st.form("not_ekle"):
        txt = st.text_input("Not yaz...")
        if st.form_submit_button("Ekle") and txt:
            veri["notlar"].append({"kim": aktif_kullanici, "metin": txt, "tarih": bugun_str})
            veri_kaydet(veri)
            st.rerun()

with tab7: # YEDEKLEME
    st.header("Bulut Yedekleme")
    st.success("Verileriniz artık otomatik olarak Google Cloud üzerinde saklanıyor.")
    
    json_verisi = json.dumps(veri, ensure_ascii=False, indent=4)
    st.download_button(
        label="📥 Güncel Verileri İndir (Manuel Yedek)",
        data=json_verisi,
        file_name=f"ekip_takip_yedek_{tr_zamani.strftime('%Y-%m-%d')}.json",
        mime="application/json"
    )
    
    if aktif_kullanici in YETKILI_KISILER:
        st.divider()
        st.subheader("Yedeği Geri Yükle")
        yd = st.file_uploader("Yedek JSON dosyası seç", type=["json"])
        if yd and st.button("Yükle ve Değiştir"):
            try:
                yeni_veri = json.load(yd)
                veri_kaydet(yeni_veri)
                st.session_state["veri_cache"] = yeni_veri 
                st.success("Başarıyla yüklendi!")
                st.rerun()
            except Exception as e:
                st.error(f"Hata: {e}")
