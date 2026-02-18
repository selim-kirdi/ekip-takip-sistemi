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
    "Ferhat": "1111", "Emre": "2222", "Selim": "1234", "Mustafa": "4444",
    "Veysel": "5555", "Furkan abi": "6666", "Osman": "7777"
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
        with open(DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"gunluk_durum": {}, "cezalar": {}, "notlar": []}

def veri_kaydet
