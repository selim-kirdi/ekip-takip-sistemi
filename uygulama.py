import streamlit as st
import json
import datetime
import os
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ekip Takip", page_icon="🕌", layout="centered")

# --- CSS AYARLARI ---
st.markdown("""
<style>
    .block-container {
        padding-top: 5rem;
        padding-bottom: 5rem;
    }
    .login-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

DOSYA = "veri.json"

ekip = ["Ferhat", "Emre", "Selim", "Mustafa", "Veysel", "Furkan abi", "Osman"]
nobet_gunleri = {
    6: "Ferhat", 0: "Emre", 1: "Selim", 2: "Mustafa", 3: "Veysel", 4: "Furkan abi", 5: "Osman"
}
SIFRELER = {
    "Ferhat": "1453", "Emre": "2277", "Selim": "2007", "Mustafa": "4444",
    "Veysel": "7955", "Furkan abi": "1999", "Osman": "6583"
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

def veri_yukle():
    if os.path.exists(DOSYA):
        try:
            with open(DOSYA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"gunluk_durum": {}, "cezalar": {}, "notlar": []}
    return {"gunluk_durum": {}, "cezalar": {}, "notlar": []}

def veri_kaydet(veri):
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

veri = veri_yukle()
bugun_str = str(datetime.date.today())

# Veri Kontrolleri
if "gunluk_durum" not in veri: veri["gunluk_durum"] = {}
if "cezalar" not in veri: veri["cezalar"] = {}
if "notlar" not in veri: veri["notlar"] = []

if bugun_str not in veri["gunluk_durum"]:
    veri["gunluk_durum"][bugun_str] = {kisi: {"risale": False, "yasin": False, "teravih": False} for kisi in ekip}
    veri_kaydet(veri)

otuz_gun_once = str(datetime.date.today() - datetime.timedelta(days=30))
kayitli_tarihler = sorted(list(veri["gunluk_durum"].keys()))
for eski_tarih in kayitli_tarihler:
    if eski_tarih < otuz_gun_once: del veri["gunluk_durum"][eski_tarih]

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

# --- ÜST BAR ---
col_header, col_logout = st.columns([7, 3])
with col_header:
    st.markdown(f"### 👋 Hoş geldin, {aktif_kullanici}")
with col_logout:
    if st.button("Çıkış Yap", use_container_width=True):
        st.session_state["giris_yapan"] = None
        st.query_params.clear()
        st.rerun()

# --- YENİ TAB EKLENDİ: YEDEKLEME ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🛡️ Nöbet", "📚 Görev", "⚖️ Ceza", "📊 İstatistik", "🧹 Temizlik", "📝 Notlar", "💾 Yedekle"])

with tab1:
    bugun_index = datetime.datetime.now().weekday()
    gunun_nobetcisi = nobet_gunleri[bugun_index]
    st.markdown(f"""
    <div style="background-color:#d4edda;padding:20px;border-radius:10px;text-align:center;border:2px solid #c3e6cb;">
        <h3 style="color:#155724;margin:0;">Bugünün Nöbetçisi</h3>
        <h1 style="color:#155724;font-size:40px;">{gunun_nobetcisi.upper()}</h1>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.header(f"Görevler ({bugun_str})")
    for kisi in ekip:
        with st.container():
            st.markdown(f"**👤 {kisi}**")
            kutu_kilitli_mi = (kisi != aktif_kullanici)
            col1, col2, col3 = st.columns(3)
            g_verisi = veri["gunluk_durum"][bugun_str][kisi]
            
            with col1: r_durum = st.checkbox("📖 Risale", value=g_verisi.get("risale", False), key=f"r_{kisi}", disabled=kutu_kilitli_mi)
            with col2: y_durum = st.checkbox("📿 Yasin", value=g_verisi.get("yasin", False), key=f"y_{kisi}", disabled=kutu_kilitli_mi)
            with col3: t_durum = st.checkbox("🕌 Teravih", value=g_verisi.get("teravih", False), key=f"t_{kisi}", disabled=kutu_kilitli_mi)
                
            if r_durum != g_verisi.get("risale") or y_durum != g_verisi.get("yasin") or t_durum != g_verisi.get("teravih"):
                veri["gunluk_durum"][bugun_str][kisi]["risale"] = r_durum
                veri["gunluk_durum"][bugun_str][kisi]["yasin"] = y_durum
                veri["gunluk_durum"][bugun_str][kisi]["teravih"] = t_durum
                veri_kaydet(veri)
                st.rerun()
            st.divider()

with tab3:
    st.subheader("Aktif Cezalar")
    aktif_ceza_var = False
    for kisi, ceza_listesi in veri.get("cezalar", {}).items():
        for i, ceza in enumerate(ceza_listesi):
            if not ceza.get("tamamlandi", False):
                aktif_ceza_var = True
                col1, col2 = st.columns([8, 3])
                with col1: st.error(f"**{kisi}:** {ceza['neden']}")
                with col2:
                    if aktif_kullanici == kisi or aktif_kullanici in YETKILI_KISILER:
                        if st.button("Tamamla", key=f"ct_{kisi}_{i}"):
                            ceza["tamamlandi"] = True
                            veri_kaydet(veri)
                            st.rerun()
    if not aktif_ceza_var: st.success("Herkes temiz! Ceza yok.")
    
    if aktif_kullanici in YETKILI_KISILER:
        st.divider()
        st.caption("Yetkili Paneli")
        with st.form("ceza_form"):
            c_col1, c_col2 = st.columns([1, 2])
            with c_col1: ck = st.selectbox("Kime?", ekip)
            with c_col2: cn = st.text_input("Nedeni?")
            if st.form_submit_button("Cezayı Yaz"):
                if cn:
                    if ck not in veri["cezalar"]: veri["cezalar"][ck] = []
                    veri["cezalar"][ck].append({"neden": cn, "tarih": bugun_str, "tamamlandi": False})
                    veri_kaydet(veri)
                    st.success("Yazıldı!")
                    st.rerun()

with tab4:
    st.subheader("📊 30 Günlük Özet")
    if aktif_kullanici in YETKILI_KISILER:
        toplam_gun = len(veri["gunluk_durum"])
        st.info(f"Kayıtlı Gün Sayısı: **{toplam_gun}**")
        
        for kisi in ekip:
            r_say, y_say, t_say = 0, 0, 0
            for tarih in veri["gunluk_durum"]:
                d = veri["gunluk_durum"][tarih].get(kisi, {})
                if d.get("risale"): r_say += 1
                if d.get("yasin"): y_say += 1
                if d.get("teravih"): t_say += 1
            
            with st.expander(f"👤 {kisi} - Detaylar"):
                m1, m2, m3 = st.columns(3)
                m1.metric("Risale", f"{r_say} / {toplam_gun}", f"-{toplam_gun-r_say} Eksik")
                m2.metric("Yasin", f"{y_say} / {toplam_gun}", f"-{toplam_gun-y_say} Eksik")
                m3.metric("Teravih", f"{t_say} / {toplam_gun}", f"-{toplam_gun-t_say} Eksik")
        
        st.divider()
        st.subheader("⚖️ Ceza Geçmişi")
        for kisi in ekip:
            ceza_listesi = veri.get("cezalar", {}).get(kisi, [])
            if ceza_listesi:
                with st.expander(f"📌 {kisi} - Ceza Kayıtları"):
                    for c in ceza_listesi:
                        ikon = "✅ Tamamlandı" if c.get("tamamlandi") else "❌ Bekliyor"
                        st.write(f"**{ikon}** - {c['neden']} *({c['tarih']})*")
        
        st.divider()
        st.warning("⚠️ Tehlikeli Bölge")
        if st.button("Tüm Verileri ve İstatistikleri Sıfırla", type="primary"):
            veri["gunluk_durum"] = {}
            veri["cezalar"] = {}
            veri_kaydet(veri)
            st.success("Sıfırlandı!")
            st.rerun()
    else:
        st.warning("Bu alanı sadece yetkililer görebilir.")

with tab5:
    st.subheader("🧹 Temizlik Programı")
    yh = datetime.datetime.now().isocalendar()[1]
    index = yh % 6
    ap = temizlik_programi[index]
    st.info(f"📍 **Şu anki Hafta: {ap['Hafta']}**")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"**🚿 Banyo:**\n{ap['Banyo']}")
        st.markdown(f"**🚽 Tuvalet:**\n{ap['Tuvalet']}")
    with col_t2:
        st.markdown(f"**🍽️ Mutfak:**\n{ap['Mutfak']}")
        st.markdown(f"**🛋️ Salon:**\n{ap['Salon']}")
    st.error(f"😴 **İzinli:** {ap['İzinli']}")
    st.divider()
    st.caption("📅 Tüm Haftaların Programı")
    df_temizlik = pd.DataFrame(temizlik_programi)
    st.dataframe(df_temizlik, hide_index=True, use_container_width=True)

with tab6:
    st.header("Ortak Notlar")
    notlar_listesi = veri.get("notlar", [])
    for i, not_verisi in enumerate(notlar_listesi):
        col1, col2 = st.columns([8, 1])
        with col1:
            if isinstance(not_verisi, dict):
                st.info(f"**{not_verisi['kim']}:** {not_verisi['metin']}")
            else: st.info(not_verisi)
        with col2:
            if isinstance(not_verisi, dict) and not_verisi['kim'] == aktif_kullanici:
                if st.button("🗑️", key=f"nsil_{i}"):
                    veri["notlar"].pop(i)
                    veri_kaydet(veri)
                    st.rerun()
    with st.form("not_form"):
        yeni_not = st.text_input("Notunuzu yazın...")
        if st.form_submit_button("Paylaş"):
            if yeni_not:
                yeni_not_objesi = {"kim": aktif_kullanici, "metin": yeni_not, "tarih": bugun_str}
                veri["notlar"].append(yeni_not_objesi)
                veri_kaydet(veri)
                st.rerun()

# --- YENİ EKLENEN YEDEKLEME SEKMESİ ---
with tab7:
    st.header("💾 Veri Yedekleme (Kurtarıcı)")
    st.info("Eğer site sıfırlanırsa verileri kaybetmemek için buradan yedek al!")
    
    # 1. VERİYİ İNDİRME BUTONU
    json_verisi = json.dumps(veri, ensure_ascii=False, indent=4)
    tarih_saat = datetime.datetime.now().strftime("%Y-%m-%d")
    st.download_button(
        label="📥 Güncel Verileri İndir (Yedekle)",
        data=json_verisi,
        file_name=f"ekip_takip_yedek_{tarih_saat}.json",
        mime="application/json"
    )
    
    st.divider()
    
    # 2. VERİYİ GERİ YÜKLEME KUTUSU (Sadece Yetkililer)
    if aktif_kullanici in YETKILI_KISILER:
        st.subheader("📤 Yedeği Geri Yükle")
        st.warning("DİKKAT: Dosya yüklersen şu anki verilerin silinir ve yüklediğin dosyadaki veriler geçerli olur.")
        
        yuklenen_dosya = st.file_uploader("Elinizdeki yedek .json dosyasını buraya bırakın", type=["json"])
        
        if yuklenen_dosya is not None:
            if st.button("Verileri Kurtar / Yükle"):
                try:
                    eski_veri = json.load(yuklenen_dosya)
                    veri_kaydet(eski_veri)
                    st.success("Veriler başarıyla kurtarıldı! Sayfa yenileniyor...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Hata oluştu! Dosya bozuk olabilir. Hata: {e}")
    else:
        st.caption("Veri yükleme işlemi sadece yetkililer içindir.")

