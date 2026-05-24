import streamlit as st
import math

# --- SEITEN-SETUP ---
st.set_page_config(page_title="Feld-Assistent GW", page_icon="🛠️", layout="centered")
st.title("🛠️ Grundwasser Feld-Assistent")
st.write("Wählen Sie das benötigte Werkzeug über die Reiter aus:")

# --- KARTEIREITER (TABS) ERSTELLEN ---
tab1, tab2, tab3 = st.tabs(["💧 DIN-Rechner", "🪨 Filterkies", "⏱️ Förderstrom"])

# ==========================================
# WERKZEUG 1: DIN-RECHNER (ROHRVOLUMEN)
# ==========================================
with tab1:
    st.subheader("Rohrvolumen nach DIN 38402-13")
    
    # Eingabefelder (mit eindeutigen 'key' Parametern, damit Streamlit sie nicht verwechselt)
    durchmesser_mm = st.number_input("Rohr-Durchmesser in mm", value=100.0, step=10.0, key="din_dn")
    tiefe_m = st.number_input("Gesamttiefe in m", value=22.5, step=0.1, key="din_tiefe")
    ruhewasser_m = st.number_input("Ruhewasserstand in m", value=14.2, step=0.1, key="din_rws")
    
    if st.button("DIN-Volumen berechnen", type="primary", key="btn_din"):
        radius_m = (durchmesser_mm / 2) / 1000
        wassersaeule_m = tiefe_m - ruhewasser_m
        
        if wassersaeule_m < 0:
            st.error("❌ Fehler: Ruhewasserstand tiefer als Gesamttiefe!")
        else:
            standwasser_volumen = math.pi * (radius_m ** 2) * wassersaeule_m * 1000
            abpump_volumen = 3 * standwasser_volumen
            
            st.success("✅ Berechnung erfolgreich!")
            col1, col2, col3 = st.columns(3)
            col1.metric("Wassersäule", f"{wassersaeule_m:.2f} m")
            col2.metric("1-fach Volumen", f"{standwasser_volumen:.1f} L")
            col3.metric("3-fach Abpumpen", f"{abpump_volumen:.1f} L")


# ==========================================
# WERKZEUG 2: FILTERKIES-RECHNER
# ==========================================
with tab2:
    st.subheader("Volumen der Filterkiesschüttung")
    
    durchmesser_m = st.number_input("Bohrlochdurchmesser in Metern (z.B. 0.15)", min_value=0.0, value=0.15, step=0.01, key="kies_dn")
    maechtigkeit_m = st.number_input("Mächtigkeit der Schüttung in Metern", min_value=0.0, value=5.0, step=0.1, key="kies_h")
    
    if st.button("Kies-Volumen berechnen", type="primary", key="btn_kies"):
        if durchmesser_m <= 0 or maechtigkeit_m <= 0:
            st.error("❌ Fehler: Bitte Werte größer als 0 eingeben.")
        else:
            radius_m = durchmesser_m / 2
            zylinder_volumen_m3 = math.pi * (radius_m ** 2) * maechtigkeit_m
            ziel_volumen_m3 = zylinder_volumen_m3 * 1.5
            
            st.success("✅ Berechnung erfolgreich!")
            col1, col2 = st.columns(2)
            col1.metric("1-fach Volumen", f"{zylinder_volumen_m3:.3f} m³", f"≙ {zylinder_volumen_m3 * 1000:.1f} L", delta_color="off")
            col2.metric("1,5-fach Abpumpen", f"{ziel_volumen_m3:.3f} m³", f"≙ {ziel_volumen_m3 * 1000:.1f} L", delta_color="normal")


# ==========================================
# WERKZEUG 3: FÖRDERSTROM-UMRECHNER
# ==========================================
with tab3:
    st.subheader("Umrechnung von Pumpenleistung & Messzeit")
    
    auswahl = st.radio(
        "Gemessener Wert:",
        ["Liter pro Minute (l/min)", "Liter pro Stunde (l/h)", "Zeit für 1 Liter (s/l)"],
        key="strom_radio"
    )
    
    l_min = 0.0
    l_h = 0.0
    sek_pro_liter = 0.0
    
    # Dynamische Felder je nach Auswahl
    if auswahl == "Liter pro Minute (l/min)":
        wert = st.number_input("Wert in l/min:", min_value=0.001, value=10.0, step=0.5, key="strom_min")
        l_min = wert
        l_h = wert * 60
        sek_pro_liter = 60 / wert
        
    elif auswahl == "Liter pro Stunde (l/h)":
        wert = st.number_input("Wert in l/h:", min_value=0.001, value=600.0, step=10.0, key="strom_h")
        l_h = wert
        l_min = wert / 60
        sek_pro_liter = 3600 / wert
        
    elif auswahl == "Zeit für 1 Liter (s/l)":
        wert = st.number_input("Sekunden für 1 Liter:", min_value=0.001, value=6.0, step=0.5, key="strom_s")
        sek_pro_liter = wert
        l_min = 60 / wert
        l_h = 3600 / wert
        
    st.write("---")
    st.success("✅ Umrechnungswerte:")
    col1, col2, col3 = st.columns(3)
    col1.metric("l / min", f"{l_min:.2f}")
    col2.metric("l / h", f"{l_h:.0f}")
    col3.metric("s / l", f"{sek_pro_liter:.2f}")
    
