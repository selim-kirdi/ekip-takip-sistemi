import streamlit as st
import json
import datetime
import os
import pandas as pd # Yeni istatistik görünümü için gerekli

# --- RENK KODLARI KALDIRILDI, ESKİ SADE HALİNE DÖNÜLDÜ ---

DOSYA = "veri.json"

ekip = ["Ferhat", "Emre", "Selim", "Mustafa", "Veysel", "Furkan abi", "Osman"]
nobet_gunleri = {
    6: "Ferhat", 0: "Emre", 1: "Selim", 2: "Mustafa", 3: "Veysel", 4: "Furkan abi", 5: "Osman"
}
SIFRELER = {
    "Ferhat": "1111", "Emre": "2222", "Selim": "1234", "Mustafa": "4444",
    "Veysel": "5555", "Furkan abi": "6666", "Osman": "7777"
}
YETKILI_KISILER = ["Furkan abi", "Selim"]

temizlik_programi = [
    {"Hafta": "1. Hafta", "Banyo": "Ferhat", "Tuvalet": "Selim", "Mutfak": "Emre, Osman", "Salon & Koridor": "Veysel", "İzinli": "Mustafa"},
    {"Hafta": "2. Hafta", "Banyo": "Mustafa", "Tuvalet": "Ferhat", "Mutfak": "Selim, Veysel", "Salon & Koridor": "Emre", "İzinli": "Osman"},
    {"Hafta": "3. Hafta", "Banyo": "Osman", "Tuvalet": "Mustafa", "Mutfak": "Ferhat, Emre", "Salon & Koridor": "Selim", "İzinli": "Veysel"},
    {"Hafta": "4. Hafta", "Banyo": "Veysel", "Tuvalet": "Osman", "Mutfak": "Mustafa, Selim", "Salon & Koridor": "Ferhat", "İzinli": "Emre"},
    {"Hafta": "5. Hafta", "Banyo": "Emre", "Tuvalet": "Veysel", "Mutfak": "Osman, Ferhat", "Salon & Koridor": "Mustafa", "İzinli": "Selim"},
    {"Hafta": "6. Hafta", "Banyo": "Selim", "Tuvalet": "Emre", "Mutfak": "Veysel, Mustafa", "Salon & Koridor": "Osman", "İzinli": "Ferhat"}
]

def veri_yukle():
    if os.path.exists(DOSYA):
        with open(DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"gunluk_durum": {}, "cezalar": {}, "notlar": []}

def veri_kaydet(veri):
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

veri = veri_yukle()
bugun_str = str(datetime.date.today())

# Veri yapısı kontrol ve oluşturma
if "gunluk_durum" not in veri: veri["gunluk_durum"] = {}
if "cezalar" not in veri: veri["cezalar"] = {}
if "notlar" not in veri: veri["notlar"] = []

if bugun_str not in veri["gunluk_durum"]:
    veri["gunluk_durum"][bugun_str] = {kisi: {"risale": False, "yasin": False, "teravih": False} for kisi in ekip}
    veri_kaydet(veri)

# 30 Günlük Temizlik
otuz_gun_once = str(datetime.date.today() - datetime.timedelta(days=30))
kayitli_tarihler = sorted(list(veri["gunluk_durum"].keys()))
for eski_tarih in kayitli_tarihler:
    if eski_tarih < otuz_gun_once: del veri["gunluk_durum"][eski_tarih]
for kisi in list(veri["cezalar"].keys()):
    veri["cezalar"][kisi] = [c for c in veri["cezalar"][kisi] if c.get("tarih", bugun_str) >= otuz_gun_once]
veri_kaydet(veri)

# --- LOGIN SİSTEMİ ---
if "giris_yapan" not in st.session_state: st.session_state["giris_yapan"] = None
st.sidebar.title("🔐 Giriş Yap")
if st.session_state["giris_yapan"] is None:
    secilen_kisi = st.sidebar.selectbox("Kim olarak kullanıyorsun?", ["Seçiniz..."] + ekip)
    girilen_sifre = st.sidebar.text_input("Şifrenizi girin", type="password")
    if st.sidebar.button("Giriş"):
        if secilen_kisi != "Seçiniz..." and SIFRELER[secilen_kisi] == girilen_sifre:
            st.session_state["giris_yapan"] = secilen_kisi
            st.rerun()
        else: st.sidebar.error("Hatalı giriş!")
    st.warning("Giriş yapınız.")
    st.stop()

aktif_kullanici = st.session_state["giris_yapan"]
if st.sidebar.button("🚪 Çıkış Yap"):
    st.session_state["giris_yapan"] = None
    st.rerun()

# --- ANA UYGULAMA ---
st.title("📌 Ekip Takip Sistemi")
st.write(f"Hoş geldin, **{aktif_kullanici}**!")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🛡️ Nöbet", "📚 Görev", "⚖️ Ceza", "📝 Notlar", "📊 İstatistik", "🧹 Temizlik"])

with tab1: # NÖBET
    bugun_index = datetime.datetime.now().weekday()
    gunun_nobetcisi = nobet_gunleri[bugun_index]
    st.header("Günün Nöbetçisi")
    st.success(f"Bugünün Nöbetçisi: **{gunun_nobetcisi.upper()}**")

with tab2: # GÖREVLER
    st.header(f"Günlük Görevler ({bugun_str})")
    for kisi in ekip:
        st.subheader(f"👤 {kisi}")
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

with tab3: # CEZALAR
    st.header("Aktif Cezalar")
    aktif_ceza_var = False
    for kisi, ceza_listesi in veri.get("cezalar", {}).items():
        for i, ceza in enumerate(ceza_listesi):
            if not ceza.get("tamamlandi", False):
                aktif_ceza_var = True
                col1, col2 = st.columns([8, 2])
                with col1: st.warning(f"**{kisi}:** {ceza['neden']} ({ceza['tarih']})")
                with col2:
                    if aktif_kullanici == kisi or aktif_kullanici in YETKILI_KISILER:
                        if st.button("Tamamla", key=f"ct_{kisi}_{i}"):
                            ceza["tamamlandi"] = True
                            veri_kaydet(veri)
                            st.rerun()
    if not aktif_ceza_var: st.info("Aktif ceza yok.")
    st.divider()
    if aktif_kullanici in YETKILI_KISILER:
        st.subheader("Yeni Ceza Yaz")
        ck = st.selectbox("Kime?", ekip)
        cn = st.text_input("Nedeni?")
        if st.button("Ekle"):
            if cn:
                if ck not in veri["cezalar"]: veri["cezalar"][ck] = []
                veri["cezalar"][ck].append({"neden": cn, "tarih": bugun_str, "tamamlandi": False})
                veri_kaydet(veri)
                st.rerun()

with tab4: # NOTLAR
    st.header("Ortak Notlar")
    notlar_listesi = veri.get("notlar", [])
    for i, not_verisi in enumerate(notlar_listesi):
        col1, col2 = st.columns([9, 1])
        with col1:
            if isinstance(not_verisi, dict):
                st.info(f"**{not_verisi['kim']}** ({not_verisi['tarih']}):\n{not_verisi['metin']}")
            else: st.info(not_verisi)
        with col2:
            if isinstance(not_verisi, dict) and not_verisi['kim'] == aktif_kullanici:
                if st.button("🗑️", key=f"nsil_{i}"):
                    veri["notlar"].pop(i)
                    veri_kaydet(veri)
                    st.rerun()
    st.divider()
    yeni_not_metni = st.text_input("Yeni not ekle")
    if st.button("Paylaş"):
        if yeni_not_metni:
            yeni_not_objesi = {"kim": aktif_kullanici, "metin": yeni_not_metni, "tarih": bugun_str}
            veri["notlar"].append(yeni_not_objesi)
            veri_kaydet(veri)
            st.rerun()

with tab5: # İSTATİSTİKLER (YENİ TASARIM - SADE)
    st.header("📊 30 Günlük Durum")
    if aktif_kullanici in YETKILI_KISILER:
        toplam_gun = len(veri["gunluk_durum"])
        st.caption(f"Son {toplam_gun} günün kayıtları baz alınmıştır.")

        for kisi in ekip:
            st.subheader(f"👤 {kisi}")
            r_say, y_say, t_say = 0, 0, 0
            for tarih in veri["gunluk_durum"]:
                d = veri["gunluk_durum"][tarih].get(kisi, {})
                if d.get("risale"): r_say += 1
                if d.get("yasin"): y_say += 1
                if d.get("teravih"): t_say += 1
            
            m1, m2, m3 = st.columns(3)
            m1.metric("📖 Risale", f"{r_say} / {toplam_gun}", delta=f"{toplam_gun-r_say} Kaçtı", delta_color="inverse")
            m2.metric("📿 Yasin", f"{y_say} / {toplam_gun}", delta=f"{toplam_gun-y_say} Kaçtı", delta_color="inverse")
            m3.metric("🕌 Teravih", f"{t_say} / {toplam_gun}", delta=f"{toplam_gun-t_say} Kaçtı", delta_color="inverse")
            st.divider()
            
        st.subheader("⚖️ Ceza Geçmişi")
        for kisi, cezalar in veri.get("cezalar", {}).items():
            if cezalar:
                with st.expander(f"{kisi} - Detay"):
                    for c in cezalar:
                        ikon = "✅" if c.get("tamamlandi") else "❌ Bekliyor"
                        st.write(f"{ikon} {c['neden']} ({c['tarih']})")
    else:
        st.error("Yetkisiz giriş.")

with tab6: # TEMİZLİK
    st.header("🧹 Haftalık Program")
    yh = datetime.datetime.now().isocalendar()[1]
    ap = temizlik_programi[yh % 6]
    st.success(f"📍 **{ap['Hafta']}**")
    c1, c2 = st.columns(2)
    c1.info(f"🚿 Banyo: {ap['Banyo']}\n\n🚽 Tuvalet: {ap['Tuvalet']}")
    c2.warning(f"🍽️ Mutfak: {ap['Mutfak']}\n\n🛋️ Salon: {ap['Salon & Koridor']}")
    st.error(f"😴 İzinli: {ap['İzinli']}")
    with st.expander("Tüm Programı Gör"):
        st.table(temizlik_programi)