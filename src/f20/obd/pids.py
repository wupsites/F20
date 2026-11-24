"""SAE-J1979-/ISO-15031-5-Dekodierung (Modus 01) – öffentlicher Standard.

Welche PIDs das eigene Fahrzeug unterstützt, wird ausschließlich aus den
Bitmasken der PIDs 0x00/0x20/0x40/0x60/0x80/0xA0/0xC0 gelesen. Nicht
unterstützte Werte werden in der Oberfläche als „nicht verfügbar“ angezeigt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class PidDef:
    pid: int
    key: str
    name_de: str
    unit: str
    length: int
    decode: Callable[[bytes], float | dict | str]
    lo: float | None = None
    hi: float | None = None


def _a(d: bytes) -> int:
    return d[0]


def _ab(d: bytes) -> int:
    return (d[0] << 8) | d[1]


def _trim(d: bytes) -> float:
    return round((d[0] - 128) * 100 / 128, 2)


def _o2_narrow(d: bytes) -> dict:
    return {"voltage_v": round(d[0] / 200, 3), "stft_pct": None if d[1] == 0xFF else round((d[1] - 128) * 100 / 128, 2)}


def _o2_wide_v(d: bytes) -> dict:
    return {"lambda": round(_ab(d) * 2 / 65536, 4), "voltage_v": round(((d[2] << 8) | d[3]) * 8 / 65536, 3)}


def _o2_wide_ma(d: bytes) -> dict:
    return {"lambda": round(_ab(d) * 2 / 65536, 4), "current_ma": round(((d[2] << 8) | d[3]) / 256 - 128, 3)}


def _monitor_status(d: bytes) -> dict:
    return {"mil_on": bool(d[0] & 0x80), "dtc_count": d[0] & 0x7F,
            "spark_ignition": not bool(d[1] & 0x08)}


_FUEL_SYS = {1: "Open loop (Temperatur)", 2: "Closed loop", 4: "Open loop (Last/Schub)",
             8: "Open loop (Fehler)", 16: "Closed loop mit Fehler"}

PIDS: dict[int, PidDef] = {p.pid: p for p in [
    PidDef(0x01, "monitor_status", "Monitorstatus seit Fehlerlöschen", "", 4, _monitor_status),
    PidDef(0x03, "fuel_system_status", "Kraftstoffsystem-Status", "", 2,
           lambda d: _FUEL_SYS.get(d[0], f"0x{d[0]:02X}")),
    PidDef(0x04, "engine_load", "Berechnete Motorlast", "%", 1, lambda d: round(_a(d) * 100 / 255, 1), 0, 100),
    PidDef(0x05, "coolant_temp", "Kühlmitteltemperatur", "°C", 1, lambda d: _a(d) - 40, -40, 130),
    PidDef(0x06, "stft_b1", "Kurzzeit-Kraftstoffkorrektur Bank 1", "%", 1, _trim, -25, 25),
    PidDef(0x07, "ltft_b1", "Langzeit-Kraftstoffkorrektur Bank 1", "%", 1, _trim, -25, 25),
    PidDef(0x08, "stft_b2", "Kurzzeit-Kraftstoffkorrektur Bank 2", "%", 1, _trim, -25, 25),
    PidDef(0x09, "ltft_b2", "Langzeit-Kraftstoffkorrektur Bank 2", "%", 1, _trim, -25, 25),
    PidDef(0x0A, "fuel_pressure", "Kraftstoffdruck (Überdruck)", "kPa", 1, lambda d: _a(d) * 3),
    PidDef(0x0B, "map", "Saugrohrdruck absolut", "kPa", 1, lambda d: _a(d), 0, 255),
    PidDef(0x0C, "rpm", "Drehzahl", "1/min", 2, lambda d: round(_ab(d) / 4, 1), 0, 7000),
    PidDef(0x0D, "speed", "Geschwindigkeit", "km/h", 1, lambda d: _a(d), 0, 250),
    PidDef(0x0E, "timing_advance", "Zündzeitpunkt (vor OT)", "°", 1, lambda d: _a(d) / 2 - 64, -20, 50),
    PidDef(0x0F, "iat", "Ansauglufttemperatur", "°C", 1, lambda d: _a(d) - 40, -40, 80),
    PidDef(0x10, "maf", "Luftmassenstrom", "g/s", 2, lambda d: round(_ab(d) / 100, 2), 0, 200),
    PidDef(0x11, "throttle", "Drosselklappenstellung", "%", 1, lambda d: round(_a(d) * 100 / 255, 1), 0, 100),
    PidDef(0x14, "o2_b1s1", "Lambdasonde B1S1 (Sprung)", "", 2, _o2_narrow),
    PidDef(0x15, "o2_b1s2", "Lambdasonde B1S2 (Sprung)", "", 2, _o2_narrow),
    PidDef(0x1C, "obd_standard", "OBD-Norm des Fahrzeugs", "", 1, lambda d: f"0x{d[0]:02X}"),
    PidDef(0x1F, "run_time", "Laufzeit seit Motorstart", "s", 2, lambda d: _ab(d)),
    PidDef(0x21, "dist_mil", "Strecke mit MIL an", "km", 2, lambda d: _ab(d)),
    PidDef(0x2C, "egr_cmd", "AGR Sollwert", "%", 1, lambda d: round(_a(d) * 100 / 255, 1)),
    PidDef(0x2E, "evap_purge", "Tankentlüftung Sollwert", "%", 1, lambda d: round(_a(d) * 100 / 255, 1)),
    PidDef(0x2F, "fuel_level", "Tankfüllstand", "%", 1, lambda d: round(_a(d) * 100 / 255, 1), 0, 100),
    PidDef(0x30, "warmups", "Warmlaufzyklen seit Fehlerlöschen", "", 1, lambda d: _a(d)),
    PidDef(0x31, "dist_clear", "Strecke seit Fehlerlöschen", "km", 2, lambda d: _ab(d)),
    PidDef(0x33, "baro", "Umgebungsluftdruck", "kPa", 1, lambda d: _a(d), 70, 110),
    PidDef(0x24, "o2w_b1s1_v", "Breitband-Lambda B1S1", "", 4, _o2_wide_v),
    PidDef(0x34, "o2w_b1s1", "Breitband-Lambda B1S1 (Strom)", "", 4, _o2_wide_ma),
    PidDef(0x3C, "cat_temp_b1s1", "Katalysatortemperatur B1S1", "°C", 2, lambda d: round(_ab(d) / 10 - 40, 1)),
    PidDef(0x42, "module_voltage", "Steuergerätespannung (Bordnetz)", "V", 2, lambda d: round(_ab(d) / 1000, 3), 8, 16),
    PidDef(0x43, "abs_load", "Absolute Last", "%", 2, lambda d: round(_ab(d) * 100 / 255, 1)),
    PidDef(0x44, "lambda_cmd", "Lambda-Sollwert", "λ", 2, lambda d: round(_ab(d) * 2 / 65536, 4), 0.7, 1.3),
    PidDef(0x45, "rel_throttle", "Relative Drosselklappenstellung", "%", 1, lambda d: round(_a(d) * 100 / 255, 1)),
    PidDef(0x46, "ambient_temp", "Umgebungstemperatur", "°C", 1, lambda d: _a(d) - 40, -40, 60),
    PidDef(0x47, "abs_throttle_b", "Drosselklappe absolut B", "%", 1, lambda d: round(_a(d) * 100 / 255, 1)),
    PidDef(0x49, "pedal_d", "Fahrpedal D", "%", 1, lambda d: round(_a(d) * 100 / 255, 1)),
    PidDef(0x4A, "pedal_e", "Fahrpedal E", "%", 1, lambda d: round(_a(d) * 100 / 255, 1)),
    PidDef(0x4C, "throttle_cmd", "Drosselklappe Sollwert", "%", 1, lambda d: round(_a(d) * 100 / 255, 1)),
    PidDef(0x51, "fuel_type", "Kraftstoffart", "", 1, lambda d: {1: "Benzin", 4: "Diesel"}.get(d[0], f"0x{d[0]:02X}")),
    PidDef(0x5C, "oil_temp", "Öltemperatur", "°C", 1, lambda d: _a(d) - 40, -40, 160),
    PidDef(0x5E, "fuel_rate", "Kraftstoffverbrauch (Rate)", "l/h", 2, lambda d: round(_ab(d) / 20, 2), 0, 50),
]}

SUPPORT_PIDS = (0x00, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0)


def decode_supported(base: int, data: bytes) -> set[int]:
    """Dekodiert eine 4-Byte-Bitmaske der unterstützten PIDs (base+1 … base+0x20)."""
    bits = int.from_bytes(data[:4], "big")
    return {base + i + 1 for i in range(32) if bits & (1 << (31 - i))}


def decode_pid(pid: int, data: bytes):
    p = PIDS.get(pid)
    if p is None:
        return None
    if len(data) < p.length:
        raise ValueError(f"PID 0x{pid:02X}: {len(data)} Byte statt {p.length}")
    return p.decode(data[: p.length])


# ------------------------------------------------------------ Fehlercodes
_DTC_LETTER = "PCBU"


def decode_obd_dtc(b1: int, b2: int) -> str:
    """2-Byte-OBD-DTC → z. B. 'P0420'."""
    return f"{_DTC_LETTER[b1 >> 6]}{(b1 >> 4) & 0x3}{b1 & 0xF:X}{b2 >> 4:X}{b2 & 0xF:X}"


def decode_obd_dtc_list(payload: bytes) -> list[str]:
    """Antwort auf Modus 03/07/0A (ohne Service-Byte) → DTC-Liste.

    Bei CAN steht nach dem Service-Byte die Anzahl der DTCs.
    """
    if not payload:
        return []
    count, body = payload[0], payload[1:]
    out = []
    for i in range(0, min(len(body), count * 2), 2):
        if body[i] == 0 and body[i + 1] == 0:
            continue
        out.append(decode_obd_dtc(body[i], body[i + 1]))
    return out
