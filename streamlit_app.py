import streamlit as st
import math
import time
import json

# --- SEITEN-SETUP ---
st.set_page_config(page_title="Feld-Assistent GW", page_icon="🛠️", layout="centered")

# =========================================================================
# CRASH-SCHUTZ & KAMPAGNEN-SPEICHER INITIALISIEREN
# =========================================================================
if 'kampagne_daten' not in st.session_state:
    st.session_state.kampagne_daten = []

if 'ziel_volumen' not in st.session_state:
    val = st.query_params.get('ziel_volumen', '0.0')
    st.session_state.ziel_volumen = float(val) if val else 0.0

if 'pumpen_leistung' not in st.session_state:
    val = st.query_params.get('pumpen_leistung', '0.0')
    st.session_state.pumpen_leistung = float(val) if val else 0.0

if 'pumpen_start' not in st.session_state:
    val = st.query_params.get('pumpen_start', '')
    st.session_state.pumpen_start = float(val) if (val and val != 'None') else None

if 'messungen' not in st.session_state:
    val = st.query_params.get('messungen', '[]')
    try:
        st.session_state.messungen = json.loads(val) if val else []
    except:
        st.session_state.messungen = []

if 'messstelle' not in st.session_state:
    st.session_state.messstelle = st.query_params.get('messstelle', '')

if 'auftragsnummer' not in st.session_state:
    st.session_state.auftragsnummer = st.query_params.get('auftragsnummer', '')

if 'pumpe_tiefe' not in st.session_state:
    val = st.query_params.get('pumpe_tiefe', '20.0')
    st.session_state.pumpe_tiefe = float(val) if val else 20.0

if 'pumpe_typ' not in st.session_state:
    st.session_state.pumpe_typ = st.query_params.get('pumpe_typ', 'MP1 mit Schlauch')

if 'probenehmer' not in st.session_state:
    st.session_state.probenehmer = st.query_params.get('probenehmer', '')

if 'wetter_manuell' not in st.session_state:
    st.session_state.wetter_manuell = st.query_params.get('wetter_manuell', '')

if 'faerbung' not in st.session_state:
    st.session_state.faerbung = st.query_params.get('faerbung', '')

if 'truebung' not in st.session_state:
    st.session_state.truebung = st.query_params.get('truebung', '')

if 'geruch' not in st.session_state:
    st.session_state.geruch = st.query_params.get('geruch', '')

if 'bodensatz' not in st.session_state:
    st.session_state.bodensatz = st.query_params.get('bodensatz', '')

if 'bemerkungen' not in st.session_state:
    st.session_state.bemerkungen = st.query_params.get('bemerkungen', '')

if 'din_tiefe' not in st.session_state:
    val = st.query_params.get('din_tiefe', '22.5')
    st.session_state.din_tiefe = float(val) if val else 22.5

if 'din_rws' not in st.session_state:
    val = st.query_params.get('din_rws', '14.2')
    st.session_state.din_rws = float(val) if val else 14.2

# =========================================================================
# SEITENLEISTE: KAMPAGNEN-VERWALTUNG (ZUSAMMENFASSUNG FÜR DAS LABOR)
# =========================================================================
with st.sidebar:
    st.header("📋 Labor-Kampagne")
    st.write("Hier werden alle Messstellen des aktuellen Auftrags gesammelt.")
    
    # Einzigartige bereits gesicherte Messstellen anzeigen
    if st.session_state.kampagne_daten:
        gespeicherte_gws = list(set([d["Messstelle"] for d in st.session_state.kampagne_daten]))
        st.success(f"Gesichert: {len(gespeicherte_gws)} Messstelle(n)")
        for gw in gespeicherte_gws:
            st.write(f"🔹 {gw}")
        
        st.write("---")
        # Generierung der Labor-Sammel-CSV (KORRIGIERT: Jetzt inklusive Pumpe, Tiefe & Förderstrom)
        labor_csv = "Auftragsnummer;Messstelle;Probenehmer;Witterung;Pumpe_Typ;Pumpe_Tiefe_m;Foerderstrom_l_min;Faerbung;Truebung;Geruch;Bodensatz;Bemerkungen;Datum;Uhrzeit;Zeit_Min;Wasserstand_m;Temp_C;pH;LF_uS_cm;Redox_mV;O2_mg_l;Status\n"
        for zeile in st.session_state.kampagne_daten:
            labor_csv += (
                f"{zeile['Auftragsnummer']};{zeile['Messstelle']};{zeile['Probenehmer']};{zeile['Witterung']};"
                f"{zeile['Pumpe_Typ']};{zeile['Pumpe_Tiefe_m']:.2f};{zeile['Foerderstrom_l_min']:.2f};"
                f"{zeile['Faerbung']};{zeile['Truebung']};{zeile['Geruch']};{zeile['Bodensatz']};{zeile['Bemerkungen']};"
                f"{zeile['Datum']};{zeile['Uhrzeit']};{zeile['Zeit_Min']};{zeile['Wasserstand_m']:.2f};"
                f"{zeile['Temp_C']:.1f};{zeile['pH']:.2f};{zeile['LF_uS_cm']:.0f};{zeile['Redox_mV']:.0f};"
                f"{zeile['O2_mg_l']:.1f};{zeile['Status']}\n"
            )
        
        st.download_button(
            label="💾 SAMMEL-CSV FÜR LABOR",
            data=labor_csv,
            file_name=f"Labor_Export_Kampagne_{st.session_state.auftragsnummer if st.session_state.auftragsnummer else 'GW'}.csv",
            mime="text/csv",
            type="primary"
        )
        
        if st.button("🗑️ Kampagnenspeicher leeren"):
            st.session_state.kampagne_daten = []
            st.rerun()
    else:
        st.info("Noch keine Messstellen zur Kampagne hinzugefügt. Nutzen Sie dazu den Button unten im Protokoll-Reiter.")

# =========================================================================
# HAUPTSEITE
# =========================================================================
st.title("🛠️ Grundwasser Feld-Assistent")
st.write("Wählen Sie das benötigte Werkzeug über die Reiter aus:")

# --- KARTEIREITER ---
tab1, tab2, tab3 = st.tabs(["💧 DIN- & Kiesrechner", "⏱️ Förderstrom", "⏳ Protokoll & Timer"])

# ==========================================
# WERKZEUG 1: DIN-RECHNER & FILTERKIES
# ==========================================
with tab1:
    st.subheader("Rohrvolumen nach DIN 38402-13")
    
    durchmesser_mm = st.number_input("Rohr-Durchmesser in mm", value=100.0, step=10.0, key="din_dn")
    tiefe_m = st.number_input("Gesamttiefe in m", value=st.session_state.din_tiefe, step=0.1)
    ruhewasser_m = st.number_input("Ruhewasserstand in m", value=st.session_state.din_rws, step=0.1)
    
    if st.button("DIN-Volumen berechnen", type="primary", key="btn_din"):
        radius_m = (durchmesser_mm / 2) / 1000
        wassersaeule_m = tiefe_m - ruhewasser_m
        
        if wassersaeule_m < 0:
            st.error("❌ Fehler: Ruhewasserstand tiefer als Gesamttiefe!")
        else:
            standwasser_volumen = math.pi * (radius_m ** 2) * wassersaeule_m * 1000
            abpump_volumen = 3 * standwasser_volumen
            
            st.session_state.din_tiefe = tiefe_m
            st.session_state.din_rws = ruhewasser_m
            st.session_state.ziel_volumen = abpump_volumen
            
            st.query_params['din_tiefe'] = str(tiefe_m)
            st.query_params['din_rws'] = str(ruhewasser_m)
            st.query_params['ziel_volumen'] = str(abpump_volumen)
            
            st.success("✅ Berechnung erfolgreich! Werte wurden im Hintergrund gespeichert.")
            col1, col2, col3 = st.columns(3)
            col1.metric("Wassersäule", f"{wassersaeule_m:.2f} m")
            col2.metric("1-fach Volumen", f"{standwasser_volumen:.1f} L")
            col3.metric("3-fach Abpumpen", f"{abpump_volumen:.1f} L")

    st.write("---")
    with st.expander("🪨 Alternativ: Filterkiesschüttung berechnen"):
        st.write("Berechnung des Volumens der Filterkiesschüttung für Sonderfälle:")
        durchmesser_m = st.number_input("Bohrlochdurchmesser in Metern", min_value=0.0, value=0.15, step=0.01, key="kies_dn")
        maechtigkeit_m = st.number_input("Mächtigkeit der Schüttung in Metern", min_value=0.0, value=5.0, step=0.1, key="kies_h")
        
        if st.button("Kies-Volumen berechnen", type="primary", key="btn_kies"):
            if durchmesser_m <= 0 or maechtigkeit_m <= 0:
                st.error("❌ Fehler: Bitte Werte größer als 0 eingeben.")
            else:
                radius_m = durchmesser_m / 2
                zylinder_volumen_m3 = math.pi * (radius_m ** 2) * maechtigkeit_m
                ziel_volumen_l = (zylinder_volumen_m3 * 1.5) * 1000
                
                st.session_state.ziel_volumen = ziel_volumen_l
                st.query_params['ziel_volumen'] = str(ziel_volumen_l)
                
                st.success("✅ Berechnung erfolgreich! Wert wurde für den Timer gespeichert.")
                col1, col2 = st.columns(2)
                col1.metric("1-fach Volumen (m³)", f"{zylinder_volumen_m3:.3f} m³")
                col2.metric("1,5-fach Abpumpen (L)", f"{ziel_volumen_l:.1f} L")


# ==========================================
# WERKZEUG 2: FÖRDERSTROM-UMRECHNER
# ==========================================
with tab2:
    st.subheader("Umrechnung von Pumpenleistung & Messzeit")
    
    auswahl = st.radio("Gemessener Wert:", ["Liter pro Minute (l/min)", "Liter pro Stunde (l/h)", "Zeit für 1 Liter (s/l)"], key="strom_radio")
    l_min, l_h, sek_pro_liter = 0.0, 0.0, 0.0
    
    if auswahl == "Liter pro Minute (l/min)":
        wert = st.number_input("Wert in l/min:", min_value=0.001, value=8.0, step=0.5, key="strom_min")
        l_min = wert
        l_h = wert * 60
        sek_pro_liter = 60 / wert
    elif auswahl == "Liter pro Stunde (l/h)":
        wert = st.number_input("Wert in l/h:", min_value=0.001, value=480.0, step=10.0, key="strom_h")
        l_h = wert
        l_min = wert / 60
        sek_pro_liter = 3600 / wert
    elif auswahl == "Zeit für 1 Liter (s/l)":
        wert = st.number_input("Sekunden für 1 Liter:", min_value=0.001, value=7.5, step=0.5, key="strom_s")
        sek_pro_liter = wert
        l_min = 60 / wert
        l_h = 3600 / wert
        
    st.write("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Liter pro Minute", f"{l_min:.2f} l/min")
    col2.metric("Liter pro Stunde", f"{l_h:.0f} l/h")
    col3.metric("Zeit für 1 Liter", f"{sek_pro_liter:.2f} s")
    
    st.write("---")
    if st.button("Förderstrom für den Timer übernehmen", type="primary", key="btn_strom"):
        st.session_state.pumpen_leistung = l_min
        st.query_params['pumpen_leistung'] = str(l_min)
        st.success(f"✅ Förderstrom von {l_min:.2f} l/min gespeichert.")


# ==========================================
# WERKZEUG 3: LIVE-TIMER & PROTOKOLL
# ==========================================
with tab3:
    st.subheader("⏳ Protokoll & Abpump-Überwachung")
    
    # Stammdaten-Block
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        messstelle_input = st.text_input("Bezeichnung der Messstelle:", value=st.session_state.messstelle)
        if messstelle_input != st.session_state.messstelle:
            st.session_state.messstelle = messstelle_input
            st.query_params['messstelle'] = messstelle_input
            st.rerun()
            
        auftragsnummer_input = st.text_input("Auftragsnummer:", value=st.session_state.auftragsnummer)
        if auftragsnummer_input != st.session_state.auftragsnummer:
            st.session_state.auftragsnummer = auftragsnummer_input
            st.query_params['auftragsnummer'] = auftragsnummer_input
            st.rerun()
            
    with col_k2:
        pumpe_tiefe_input = st.number_input("Einbautiefe Pumpe (m unter ROK):", value=st.session_state.pumpe_tiefe, step=0.1)
        if pumpe_tiefe_input != st.session_state.pumpe_tiefe:
            st.session_state.pumpe_tiefe = pumpe_tiefe_input
            st.query_params['pumpe_tiefe'] = str(pumpe_tiefe_input)
            st.rerun()

        pumpen_optionen = ["MP1 mit Schlauch", "MP1 mit Steigrohren", "Comet Pumpe mit Schlauch"]
        try:
            default_index = pumpen_optionen.index(st.session_state.pumpe_typ)
        except ValueError:
            default_index = 0
            
        pumpe_typ_input = st.selectbox("Verwendete Pumpe:", options=pumpen_optionen, index=default_index)
        if pumpe_typ_input != st.session_state.pumpe_typ:
            st.session_state.pumpe_typ = pumpe_typ_input
            st.query_params['pumpe_typ'] = pumpe_typ_input
            st.rerun()

        probenehmer_input = st.text_input("Probenehmer (Name / Kürzel):", value=st.session_state.probenehmer, placeholder="z. B. J. Müller")
        if probenehmer_input != st.session_state.probenehmer:
            st.session_state.probenehmer = probenehmer_input
            st.query_params['probenehmer'] = probenehmer_input
            st.rerun()

    wetter_input = st.text_input("Witterung / Lufttemperatur (manuelle Eingabe):", value=st.session_state.wetter_manuell, placeholder="z. B. 18°C, sonnig / trocken")
    if wetter_input != st.session_state.wetter_manuell:
        st.session_state.wetter_manuell = wetter_input
        st.query_params['wetter_manuell'] = wetter_input
        st.rerun()

    st.write("---")
    st.markdown("#### 👁️ Organoleptische Befundung")
    
    col_o1, col_o2 = st.columns(2)
    with col_o1:
        faerbung_input = st.text_input("Färbung:", value=st.session_state.faerbung, placeholder="z. B. farblos, schwach gelblich")
        if faerbung_input != st.session_state.faerbung:
            st.session_state.faerbung = faerbung_input
            st.query_params['faerbung'] = faerbung_input
            st.rerun()
            
        truebung_input = st.text_input("Trübung:", value=st.session_state.truebung, placeholder="z. B. keine, schwach trüb, stark trüb")
        if truebung_input != st.session_state.truebung:
            st.session_state.truebung = truebung_input
            st.query_params['truebung'] = truebung_input
            st.rerun()
            
    with col_o2:
        geruch_input = st.text_input("Geruch:", value=st.session_state.geruch, placeholder="z. B. geruchlos, nach H2S, moorig")
        if geruch_input != st.session_state.geruch:
            st.session_state.geruch = geruch_input
            st.query_params['geruch'] = geruch_input
            st.rerun()
            
        bodensatz_input = st.text_input("Bodensatz:", value=st.session_state.bodensatz, placeholder="z. B. kein, sandig, flockig, braun")
        if bodensatz_input != st.session_state.bodensatz:
            st.session_state.bodensatz = bodensatz_input
            st.query_params['bodensatz'] = bodensatz_input
            st.rerun()

    bemerkungen_input = st.text_area("Bemerkungen des Probenehmers:", value=st.session_state.bemerkungen, placeholder="z. B. Starke Initialtrübung, technische Auffälligkeiten o.ä.")
    if bemerkungen_input != st.session_state.bemerkungen:
        st.session_state.bemerkungen = bemerkungen_input
        st.query_params['bemerkungen'] = bemerkungen_input
        st.rerun()

    st.write("---")

    vol = st.session_state.ziel_volumen
    flow = st.session_state.pumpen_leistung
    
    if vol > 0 and flow > 0:
        total_minutes = vol / flow
        total_seconds = int(total_minutes * 60)
        
        st.info(f"**Ziel-Volumen:** {vol:.1f} L | **Förderstrom:** {flow:.2f} l/min | **Dauer:** {total_minutes:.1f} Min.")
        
        if st.session_state.pumpen_start is None:
            if st.button("▶️ Pumpe starten & Protokoll beginnen", type="primary"):
                jetzt = time.time()
                st.session_state.pumpen_start = jetzt
                st.session_state.messungen = [] 
                st.query_params['pumpen_start'] = str(jetzt)
                st.query_params['messungen'] = "[]"
                st.rerun() 
        else:
            elapsed_seconds = int(time.time() - st.session_state.pumpen_start)
            remaining_total = max(0, total_seconds - elapsed_seconds)
            
            elapsed_in_cycle = elapsed_seconds % 300
            remaining_in_cycle = 300 - elapsed_in_cycle
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.metric("Verbleibende Gesamtdauer", f"{remaining_total // 60:02d}:{remaining_total % 60:02d} Min")
                st.progress(min(1.0, elapsed_seconds / total_seconds))
            
            with col_t2:
                if remaining_in_cycle < 15 or elapsed_in_cycle < 15:
                    st.error(f"🔔 JETZT MESSEN! ({remaining_in_cycle // 60:02d}:{remaining_in_cycle % 60:02d} Min)")
                else:
                    st.metric("Nächste Parameter-Messung in", f"{remaining_in_cycle // 60:02d}:{remaining_in_cycle % 60:02d} Min")
                st.progress(min(1.0, elapsed_in_cycle / 300))
                
            if st.button("🔄 Timer-Anzeige aktualisieren"):
                st.rerun()
            
            st.write("---")
            st.markdown("### 📝 Parameter erfassen")
            
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                water_level = st.number_input("Wasserstand (m)", value=14.50, step=0.01)
                temp = st.number_input("Wasser-Temp. (°C)", value=11.0, step=0.1)
                
                wasser_ueber_pumpe = st.session_state.pumpe_tiefe - water_level
                if wasser_ueber_pumpe < 1.0:
                    st.error(f"🚨 TROCKENLAUFSCHUTZ:\nWasserstand zu niedrig! Pumpe hängt nur noch {wasser_ueber_pumpe:.2f} m im Wasser!")
                
            with col_p2:
                ph = st.number_input("pH-Wert", value=7.00, step=0.01)
                lf = st.number_input("LF (µS/cm)", value=500.0, step=1.0)
            with col_p3:
                redox = st.number_input("Redox (mV)", value=150.0, step=1.0)
                o2 = st.number_input("Sauerstoff (mg/l)", value=5.0, step=0.1)
                
            if st.button("💾 Werte zum Protokoll hinzufügen", type="primary"):
                uhrzeit_jetzt = time.strftime("%H:%M:%S")
                datum_jetzt = time.strftime("%d.%m.%Y")
                zeitstempel = f"{elapsed_seconds // 60:02d}:{elapsed_seconds % 60:02d}"
                
                warnung_text = "⚠️ < 1m Wasser!" if (st.session_state.pumpe_tiefe - water_level) < 1.0 else ""
                
                neue_messung = {
                    "Datum": datum_jetzt,
                    "Uhrzeit": uhrzeit_jetzt,
                    "Zeit (Min)": zeitstempel,
                    "Wasserstand (m)": water_level,
                    "Temp (°C)": temp,
                    "pH": ph,
                    "LF (µS/cm)": lf,
                    "Redox (mV)": redox,
                    "O2 (mg/l)": o2,
                    "Status": warnung_text
                }
                st.session_state.messungen.append(neue_messung)
                st.query_params['messungen'] = json.dumps(st.session_state.messungen)
                st.success(f"Messung um {uhrzeit_jetzt} erfolgreich gespeichert!")
                st.rerun()
                
            # --- PROTOKOLL & EXPORT ---
            if len(st.session_state.messungen) > 0:
                st.write("---")
                st.markdown("### 📋 Ihr digitales Messprotokoll")
                
                tabellen_daten = list(st.session_state.messungen)
                
                if len(st.session_state.messungen) >= 2:
                    m_letzte = st.session_state.messungen[-1]
                    m_vorletzte = st.session_state.messungen[-2]
                    def prozent_diff(neu, alt):
                        return ((neu - alt) / alt) * 100 if alt != 0 else 0.0
                    
                    abweichung_zeile = {
                        "Datum": "-", "Uhrzeit": "Δ Vorwert", "Zeit (Min)": "-",
                        "Wasserstand (m)": f"{prozent_diff(m_letzte['Wasserstand (m)'], m_vorletzte['Wasserstand (m)']):+.1f}%",
                        "Temp (°C)": f"{prozent_diff(m_letzte['Temp (°C)'], m_vorletzte['Temp (°C)']):+.1f}%",
                        "pH": f"{prozent_diff(m_letzte['pH'], m_vorletzte['pH']):+.1f}%",
                        "LF (µS/cm)": f"{prozent_diff(m_letzte['LF (µS/cm)'], m_vorletzte['LF (µS/cm)']):+.1f}%",
                        "Redox (mV)": f"{prozent_diff(m_letzte['Redox (mV)'], m_vorletzte['Redox (mV)']):+.1f}%",
                        "O2 (mg/l)": f"{prozent_diff(m_letzte['O2 (mg/l)'], m_vorletzte['O2 (mg/l)']):+.1f}%",
                        "Status": ""
                    }
                    tabellen_daten = tabellen_daten + [abweichung_zeile]
                
                st.dataframe(tabellen_daten)
                
                bezeichnung = st.session_state.messstelle if st.session_state.messstelle else "Nicht_angegeben"
                auftrag = st.session_state.auftragsnummer if st.session_state.auftragsnummer else "Nicht_angegeben"
                wetter_wert = st.session_state.wetter_manuell if st.session_state.wetter_manuell else "Keine Angabe"
                probenehmer_wert = st.session_state.probenehmer if st.session_state.probenehmer else "Nicht angegeben"
                faerbung_wert = st.session_state.faerbung if st.session_state.faerbung else "Keine Angabe"
                truebung_wert = st.session_state.truebung if st.session_state.truebung else "Keine Angabe"
                geruch_wert = st.session_state.geruch if st.session_state.geruch else "Keine Angabe"
                bodensatz_wert = st.session_state.bodensatz if st.session_state.bodensatz else "Keine Angabe"
                bemerkungen_wert = st.session_state.bemerkungen if st.session_state.bemerkungen else "Keine"
                csv_safe_bemerkungen = bemerkungen_wert.replace("\n", " // ")

                # --- NEU: BUTTON UM DIESE MESSSTELLE ZUR KAMPAGNE HINZUZUFÜGEN ---
                st.write("---")
                st.markdown("### 📦 Kampagnen-Sicherung")
                if st.button("➕ DIESE Messstelle zur Labor-Kampagne hinzufügen", type="secondary"):
                    # Für jede zeitliche Messung dieser Messstelle eine flache Zeile erzeugen
                    for m in st.session_state.messungen:
                        # KORRIGIERT: Hier werden jetzt Pumpe_Typ, Pumpe_Tiefe_m und Foerderstrom_l_min explizit mitgesichert
                        sammel_zeile = {
                            "Auftragsnummer": auftrag, "Messstelle": bezeichnung, "Probenehmer": probenehmer_wert,
                            "Witterung": wetter_wert, 
                            "Pumpe_Typ": st.session_state.pumpe_typ,
                            "Pumpe_Tiefe_m": st.session_state.pumpe_tiefe,
                            "Foerderstrom_l_min": st.session_state.pumpen_leistung,
                            "Faerbung": faerbung_wert, "Truebung": truebung_wert,
                            "Geruch": geruch_wert, "Bodensatz": bodensatz_wert, "Bemerkungen": csv_safe_bemerkungen,
                            "Datum": m["Datum"], "Uhrzeit": m["Uhrzeit"], "Zeit_Min": m["Zeit (Min)"],
                            "Wasserstand_m": m["Wasserstand (m)"], "Temp_C": m["Temp (°C)"], "pH": m["pH"],
                            "LF_uS_cm": m["LF (µS/cm)"], "Redox_mV": m["Redox (mV)"], "O2_mg_l": m["O2 (mg/l)"],
                            "Status": m["Status"]
                        }
                        st.session_state.kampagne_daten.append(sammel_zeile)
                    st.success(f"✅ Alle Daten für die Messstelle {bezeichnung} wurden links in der Sammel-Kampagne gespeichert!")
                    st.rerun()

                # Einzel-Anzeige Text-Protokoll
                protokoll_text = f"=== MESSSTELLEN-PROTOKOLL: {bezeichnung} ===\n"
                protokoll_text += f"Auftragsnummer: {auftrag} | Probenehmer: {probenehmer_wert}\n"
                protokoll_text += f"Witterung: {wetter_wert} | Färbung: {faerbung_wert} | Trübung: {truebung_wert} | Geruch: {geruch_wert} | Bodensatz: {bodensatz_wert}\n"
                protokoll_text += f"Bemerkungen: {bemerkungen_wert}\n"
                protokoll_text += "-"*102 + "\n"
                st.code(protokoll_text, language="markdown")
                
            # --- RESET-BUTTON (FÜR NÄCHSTE MESSSTELLE) ---
            st.write("---")
            if st.button("🗑️ Einzelne Messstelle zurücksetzen (Nächste Messstelle anfahren)", type="secondary"):
                st.session_state.ziel_volumen = 0.0
                st.session_state.pumpen_leistung = 0.0
                st.session_state.pumpen_start = None
                st.session_state.messungen = []
                st.session_state.messstelle = ""
                st.session_state.faerbung = ""
                st.session_state.truebung = ""
                st.session_state.geruch = ""
                st.session_state.bodensatz = ""
                st.session_state.bemerkungen = ""
                st.query_params.clear()
                st.rerun()
                
            if 'remaining_total' in locals() and remaining_total == 0:
                st.balloons()
                st.success("🎉 Das berechnete Zielvolumen wurde vollständig abgepumpt!")
    else:
        st.warning("⚠️ Bitte berechnen Sie zuerst das Abpumpvolumen (Reiter 1) und übernehmen Sie den Förderstrom (Reiter 2).")
