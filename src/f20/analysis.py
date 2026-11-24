"""Regelbasierte Auswertung von Messwerten (Motorzustand, Verbrauch).

Alle Schwellwerte sind allgemeine Diagnose-Faustregeln für Ottomotoren mit
OBD-II, KEINE BMW-Sollwerte. Jede Aussage trägt deshalb den Nachweisstatus
„likely“ (Faustregel) und eine Begründung. Abgeleitete Größen (Ladedruck,
Verbrauch) sind ausdrücklich als Schätzung gekennzeichnet.
"""

from __future__ import annotations

PETROL_AFR = 14.7          # stöchiometrisches Luft-Kraftstoff-Verhältnis Benzin (E0)
PETROL_DENSITY_G_PER_L = 745.0


def derived_values(values: dict[str, object]) -> dict[str, dict]:
    """Berechnet abgeleitete Größen aus tatsächlich gelesenen Werten."""
    out: dict[str, dict] = {}
    m, b = values.get("map"), values.get("baro")
    if isinstance(m, (int, float)) and isinstance(b, (int, float)):
        out["boost"] = {"name_de": "Ladedruck (relativ, abgeleitet)", "value": round((m - b) / 100, 2), "unit": "bar",
                        "derived_from": "MAP − Umgebungsdruck", "evidence": "likely"}
    maf, spd = values.get("maf"), values.get("speed")
    lam = values.get("lambda_cmd")
    lam = lam if isinstance(lam, (int, float)) and 0.6 < lam < 1.5 else 1.0
    if isinstance(maf, (int, float)):
        lph = maf * 3600 / (PETROL_AFR * lam * PETROL_DENSITY_G_PER_L)
        out["fuel_lph_est"] = {"name_de": "Verbrauch (Schätzung aus Luftmasse)", "value": round(lph, 2), "unit": "l/h",
                               "derived_from": "MAF / (14,7 · λ) / 745 g/l", "evidence": "likely"}
        if isinstance(spd, (int, float)) and spd >= 5:
            out["fuel_l100_est"] = {"name_de": "Momentanverbrauch (Schätzung)", "value": round(lph / spd * 100, 1),
                                    "unit": "l/100 km", "derived_from": "l/h ÷ km/h × 100", "evidence": "likely"}
    return out


def engine_findings(values: dict[str, object], running_minutes: float | None = None) -> list[dict]:
    """Auffälligkeiten nach Faustregeln. Gibt nur Hinweise, keine Diagnose."""
    f: list[dict] = []

    def add(level: str, key: str, text: str, why: str) -> None:
        f.append({"level": level, "key": key, "text_de": text, "rationale_de": why, "evidence": "likely"})

    for k, label in (("stft_b1", "Kurzzeit"), ("ltft_b1", "Langzeit")):
        v = values.get(k)
        if isinstance(v, (int, float)):
            if abs(v) > 15:
                add("warn", k, f"{label}-Gemischkorrektur {v:+.1f} % – deutlich außerhalb ±10 %.",
                    "Dauerhaft > ±10 % deutet oft auf Falschluft, Einspritz-/Kraftstoffdruck- oder Sensorprobleme hin.")
            elif abs(v) > 10:
                add("info", k, f"{label}-Gemischkorrektur {v:+.1f} % – erhöht.",
                    "Werte bis ±10 % gelten allgemein als unauffällig; Beobachtung über mehrere Fahrten empfohlen.")
    c = values.get("coolant_temp")
    if isinstance(c, (int, float)):
        if c > 115:
            add("warn", "coolant_temp", f"Kühlmittel {c:.0f} °C – sehr hoch.", "Über ~115 °C ist auch bei Kennfeldthermostat ungewöhnlich.")
        elif running_minutes is not None and running_minutes > 20 and c < 75:
            add("info", "coolant_temp", f"Kühlmittel nach {running_minutes:.0f} min erst {c:.0f} °C.",
                "Erreicht der Motor keine Betriebstemperatur, steigt der Verbrauch (Thermostat prüfen lassen).")
    u = values.get("module_voltage")
    rpm = values.get("rpm")
    if isinstance(u, (int, float)):
        if isinstance(rpm, (int, float)) and rpm > 500:
            if u < 13.0:
                add("warn", "module_voltage", f"Bordspannung {u:.2f} V bei laufendem Motor – niedrig.",
                    "Bei laufendem Motor liegt die Ladespannung typischerweise über 13 V (BMW-IBS kann zeitweise absenken).")
            elif u > 15.0:
                add("warn", "module_voltage", f"Bordspannung {u:.2f} V – hoch.", "Über 15 V ist untypisch (Laderegelung).")
        elif u < 12.2:
            add("info", "module_voltage", f"Ruhespannung {u:.2f} V – Batterie schwach geladen.",
                "Vor jeder Codiersitzung Batterie laden bzw. Erhaltungsladegerät anschließen.")
    iat, amb = values.get("iat"), values.get("ambient_temp")
    if isinstance(iat, (int, float)) and isinstance(amb, (int, float)) and iat - amb > 25 and isinstance(rpm, (int, float)) and rpm > 0:
        add("info", "iat", f"Ansaugluft {iat:.0f} °C, Umgebung {amb:.0f} °C.", "Große Differenz ist im Stand/Stau normal, in Fahrt eher nicht.")
    return f


def consumption_hints(values: dict[str, object]) -> list[str]:
    """Allgemeine, belegbare Einflussfaktoren für hohen Verbrauch anhand verfügbarer Werte."""
    hints = []
    c = values.get("coolant_temp")
    if isinstance(c, (int, float)) and c < 70:
        hints.append("Motor nicht auf Betriebstemperatur: Kurzstrecken erhöhen den Verbrauch deutlich.")
    lt = values.get("ltft_b1")
    if isinstance(lt, (int, float)) and lt > 10:
        hints.append("Positive Langzeitkorrektur: Motorsteuerung reichert dauerhaft an – Falschluft/Sensor prüfen lassen.")
    if not hints:
        hints.append("Aus den aktuell verfügbaren Werten ist keine technische Ursache erkennbar. "
                     "Fahrprofil (Kurzstrecke, Stadt), Reifendruck und Beladung sind häufige Faktoren.")
    return hints
