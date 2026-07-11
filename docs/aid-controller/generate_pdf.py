#!/usr/bin/env python3
"""Generate AID Pendant Controller hardware plan PDF with manufacturer images."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "images"
OUT = ROOT / "AID_Pendant_Controller_Hardware_Plan.pdf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class PlanPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"AID Pendant Controller - {date.today().isoformat()} - oldal {self.page_no()}", align="C")


def section(pdf: PlanPDF, title: str):
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)


def body(pdf: PlanPDF, text: str):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 5, text)
    pdf.ln(1)


def bullet(pdf: PlanPDF, items: list[str]):
    pdf.set_font("DejaVu", "", 10)
    for item in items:
        pdf.set_x(pdf.l_margin)
        safe = item.replace("×", "x").replace("—", "-").replace("Ø", "O")
        pdf.multi_cell(0, 5, f"  - {safe}")
    pdf.ln(1)


def bom_row(pdf: PlanPDF, cols: list[str], bold: bool = False):
    w = [8, 50, 26, 20, 12, 54]
    pdf.set_font("DejaVu", "B" if bold else "", 7 if not bold else 8)
    for c, width in zip(cols, w):
        txt = c.replace("Ø", "O").replace("×", "x")
        pdf.cell(width, 6, txt[:40], border=1)
    pdf.ln()


def add_image_block(pdf: PlanPDF, path: Path, caption: str, url: str, w: float = 42):
    pdf.set_x(pdf.l_margin)
    if path.exists() and path.stat().st_size > 5000:
        try:
            pdf.image(str(path), w=w)
            pdf.ln(2)
        except Exception:
            pdf.set_font("DejaVu", "", 9)
            pdf.multi_cell(0, 5, f"[Kep: {path.name}]")
    else:
        pdf.set_font("DejaVu", "", 9)
        pdf.multi_cell(0, 5, "(Kep nem elerheto offline - lasd URL)")
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 4, caption)
    pdf.set_x(pdf.l_margin)
    pdf.set_text_color(0, 0, 180)
    pdf.multi_cell(0, 4, url)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)


def build():
    pdf = PlanPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_font("DejaVu", "", FONT)
    pdf.add_font("DejaVu", "B", FONT_B)

    # --- Cover ---
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 22)
    pdf.cell(0, 14, "AID Pendant Controller", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Hardver terv — minimál méret, maximális BLE stabilitás", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    pdf.set_font("DejaVu", "", 11)
    body(
        pdf,
        "Cél: telefon- és Garmin-független, nyaklánchos inzulinvezérlő.\n"
        "Szenzor: Linx CGM (BLE, dekódolt)  |  Pumpa: Omnipod DASH  |  UI: 0,42\" OLED, csak gombra\n"
        f"Dátum: {date.today().strftime('%Y. %B %d.')}",
    )
    body(
        pdf,
        "Ajánlott platform: Nordic nRF52840 (nem ESP32) — alacsony fogyasztás, "
        "bizonyított több-BLE-central támogatás, Loop/OmniBLE ökoszisztéma.",
    )

    # --- 1. Design ---
    pdf.add_page()
    section(pdf, "1. Tervezési döntés")
    body(
        pdf,
        "A lehető legkisebb, legstabilabb és elegendően erős konfigurációhoz az nRF52840 SoC "
        "a legjobb választás. Az ESP32-C6 AMOLED lap nagyobb, több áramot fogyaszt, és a Garmin "
        "BLE kapcsolat nem megbízható folyamatos vezérlésre.",
    )
    bullet(
        pdf,
        [
            "Prototipus (Fazis 1): Seeed XIAO nRF52840 - ugyanaz a chip, konnyu fejlesztes",
            "Vegleges (Fazis 2): ISP1807-LR modul (8x8 mm) egyedi kerek PCB-n",
            "Kijelzo: 0.42 inch PMOLED (12x11 mm) - legkisebb; gombra ebred, 30 s timeout",
            "Akku: LPR363027 kerek LiPo, 225 mAh, O30 mm",
            "Garmin: nincs a kritikus utvonalon",
        ],
    )
    body(
        pdf,
        "Végső méret (tokkal): Ø35 mm × 7,5 mm  |  Súly: ~12–15 g  |  Üzemidő: 2–4 nap (kijelző alvásban)",
    )

    section(pdf, "1.1 Architektúra")
    body(
        pdf,
        "┌─────────────────────────────────────┐\n"
        "│  nRF52840 (ISP1807 / XIAO)          │\n"
        "│  ├── BLE Central → Linx CGM         │\n"
        "│  ├── BLE Central → Omnipod DASH     │\n"
        "│  ├── oref1 AID algoritmus (5 perc)  │\n"
        "│  ├── DASH keep-alive (2,5 perc)     │\n"
        "│  └── I2C → 0,42\" OLED (gombra)      │\n"
        "│  LiPo 225 mAh + mágneses töltés     │\n"
        "└─────────────────────────────────────┘",
    )

    # --- 2. BOM table ---
    pdf.add_page()
    section(pdf, "2. Alkatrészlista (BOM)")
    bom_row(pdf, ["#", "Alkatrész", "Modell", "Méret", "Db", "Beszerzés"], bold=True)
    rows = [
        ("1", "MCU modul (prod.)", "ISP1807-LR", "8×8×1 mm", "1", "insightsip.com"),
        ("2", "MCU modul (proto)", "XIAO nRF52840", "21×17.5 mm", "1", "seeedstudio.com"),
        ("3", "Kerek LiPo + PCM", "LPR363027", "Ø30×3.6", "1", "lipolbattery.com"),
        ("4", "OLED kijelző", "MLD042 / DM-OLED042", "12×11 mm", "1", "displaymodule.com"),
        ("5", "Egyedi PCB", "JLCPCB 2L", "Ø32 mm", "5", "jlcpcb.com"),
        ("6", "Tact gomb", "4×4×1.5 mm SMD", "—", "1", "LCSC / Mouser"),
        ("7", "Mágneses töltő", "2-pin pogo", "Ø8 mm", "1", "AliExpress"),
        ("8", "Fuel gauge (opc.)", "MAX17048", "1.5×2 mm", "1", "Analog Devices"),
        ("9", "LiPo töltő IC", "BQ25101", "—", "1", "XIAO-on / PCB"),
        ("10", "Tok", "3D nyomtatott", "Ø35×7.5", "1", "saját STL"),
        ("11", "Lánc + karabiner", "42 cm", "—", "1", "ékszer bolt"),
    ]
    for r in rows:
        bom_row(pdf, list(r))

    # --- 3. Images page 1 ---
    pdf.add_page()
    section(pdf, "3. Alkatrészek — gyártói fotók (1/2)")
    add_image_block(
        pdf,
        IMG / "isp1807-lr.png",
        "1. ISP1807-LR — nRF52840 BLE modul, beépített antenna (Insight SIP)",
        "https://www.insightsip.com/products/bluetooth-le-modules/isp1807",
        45,
    )
    pdf.ln(2)
    add_image_block(
        pdf,
        IMG / "xiao-nrf52840.jpg",
        "2. Seeed XIAO nRF52840 — prototípus modul (ugyanaz a SoC)",
        "https://www.seeedstudio.com/XIAO-BLE-p-5306.html",
        40,
    )
    pdf.ln(2)
    add_image_block(
        pdf,
        IMG / "blyst840.jpg",
        "2b. Alternatíva: BLYST840 modul (14×9 mm, könnyebb forrasztható)",
        "https://www.crowdsupply.com/i-syst/blyst840",
        45,
    )

    # --- Images page 2 ---
    pdf.add_page()
    section(pdf, "3. Alkatrészek — gyártói fotók (2/2)")
    add_image_block(
        pdf,
        IMG / "round-lipo.jpg",
        "3. Kerek LiPo 353027 / 363027 (~210–225 mAh, 3,7 V, PCM)",
        "https://www.lipolbattery.com/Round-LiPo-Battery.html",
        40,
    )
    pdf.ln(2)
    add_image_block(
        pdf,
        IMG / "oled042.jpg",
        "4. 0,42\" OLED 72×40, I2C, SSD1315 — legkisebb kijelző",
        "https://www.displaymodule.com/products/0-42-inch-oled-graphic-display-72x40-with-i2c",
        45,
    )
    pdf.ln(2)
    add_image_block(
        pdf,
        IMG / "round-oled075.jpg",
        "4b. Opcionális: 0,75\" kerek OLED 128×128 (nagyobb, olvashatóbb UI)",
        "https://www.szmaclight.com/oled-display-module.html",
        35,
    )

    # --- 4. Mechanical ---
    pdf.add_page()
    section(pdf, "4. Mechanikai terv")
    body(
        pdf,
        "Oldalnézet (mm):\n\n"
        "     ┌──────────────┐\n"
        "     │ 0.42\" OLED   │  1.2 mm (beépített, csak nyíláson látszik)\n"
        "     ├──────────────┤\n"
        "     │ ISP1807/PCB  │  1.0 mm\n"
        "     ├──────────────┤\n"
        "     │ LiPo Ø30mm   │  3.6 mm\n"
        "     ├──────────────┤\n"
        "     │ pogo + tok   │  1.5 mm\n"
        "     └──────────────┘\n"
        "     Összesen: ~7.5 mm vastag, Ø35 mm tok",
    )
    bullet(
        pdf,
        [
            "Anyag: PETG vagy ABS (ne fém — BLE antenna a PCB szélén)",
            "Antenna keep-out: ISP1807 körül min. 5 mm üres terület",
            "USB/mágneses pogo: tok alján, 2× arany tű",
            "Gomb: oldalsó vagy elülső tact switch (kijelző wake)",
            "Láncszem: tok tetején 2 mm lyuk",
        ],
    )

    section(pdf, "4.1 Egyedi kerek PCB")
    body(
        pdf,
        "A kerek PCB nem kapható készben. JLCPCB / PCBWay: Gerber feltöltés, Ø32 mm board outline.\n"
        "Prototípus előtt: XIAO nRF52840 téglalap PCB tokban — nem kell azonnal kerek PCB.",
    )

    # --- 5. Power ---
    pdf.add_page()
    section(pdf, "5. Áramellátás és üzemidő")
    bom_row(pdf, ["Állapot", "Átlag áram", "Megjegyzés"], bold=True)
    for r in [
        ("Kijelző OFF, 2× BLE", "2.5–4 mA", "nRF52840 + NimBLE, WiFi nincs"),
        ("Kijelző ON (30 mp/óra)", "+2 mA átlag", "OLED ~8 mA csúcs"),
        ("DASH keep-alive", "impulzus 5 mpként", "2.5 percenként parancs"),
    ]:
        bom_row(pdf, list(r))
    pdf.ln(2)
    body(
        pdf,
        "225 mAh akku, 3.5 mA átlag, 80% hatásfok → ~51 óra (~2.1 nap).\n"
        "300 mAh akku → ~2.9 nap. Ajánlott: LPR363027 (225 mAh) vagy nagyobb LPR283535 (300 mAh, +0.5 mm).",
    )

    section(pdf, "5.1 Miért nem ESP32-C6 AMOLED?")
    bullet(
        pdf,
        [
            "Ø40 mm vs Ø35 mm — nagyobb medál",
            "AMOLED + ESP32: 3–8 mA minimum vs nRF 2.5–4 mA",
            "DASH/OmniBLE port elsősorban nRF/Arduino környezetben",
            "Garmin BLE nem folyamatos — kijelzővel sem oldható meg megbízhatóan",
        ],
    )

    # --- 6. Firmware ---
    section(pdf, "6. Firmware modulok (FreeRTOS / Zephyr)")
    bom_row(pdf, ["Task", "Prioritás", "Feladat"], bold=True)
    for r in [
        ("dash_keepalive", "Magas", "2.5 percenként BLE ping a DASH podnak"),
        ("linx_ble", "Magas", "Glucose stream olvasás, dekódolás"),
        ("aid_loop", "Közepes", "oref1, 5 percenként temp basal számítás"),
        ("dash_cmd", "Magas", "Bolus / temp basal végrehajtás"),
        ("ui_oled", "Alacsony", "Gombra: glucose, IOB, bolus UI; 30 s sleep"),
        ("safety", "Kritikus", "Max U/óra, hypó suspend, watchdog"),
    ]:
        bom_row(pdf, list(r))

    # --- 7. Phases ---
    pdf.add_page()
    section(pdf, "7. Fejlesztési fázisok")
    phases = [
        ("Fázis 1 — Proto", "XIAO + breadboard/DASH teszt", "DASH BLE 24 h stabil"),
        ("Fázis 2 — Linx", "Linx driver port nRF-re", "Glucose stream 5 perc"),
        ("Fázis 3 — Loop", "oref1 + safety", "Szimulált basal"),
        ("Fázis 4 — UI", "0.42\" OLED + gomb", "Bolus kijelzőről"),
        ("Fázis 5 — Mini", "ISP1807 + kerek PCB + tok", "Hordható medál"),
    ]
    for name, task, gate in phases:
        body(pdf, f"{name}\n  Feladat: {task}\n  Kapu: {gate}\n")

    section(pdf, "8. Beszerzési linkek (összefoglaló)")
    links = [
        "ISP1807: https://www.insightsip.com/shop-online/product/38-isp1807-lr",
        "XIAO nRF52840: https://www.seeedstudio.com/XIAO-BLE-p-5306.html",
        "Kerek LiPo: https://www.lipolbattery.com/Round-LiPo-Battery.html",
        "0.42\" OLED: https://www.displaymodule.com/products/0-42-inch-oled-graphic-display-72x40-with-i2c",
        "PCB: https://jlcpcb.com",
        "DASH protokoll ref: https://github.com/LoopKit/OmniBLE",
        "nRF52840 DK docs: https://docs.nordicsemi.com/",
    ]
    for link in links:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("DejaVu", "", 8)
        pdf.set_text_color(0, 0, 180)
        pdf.multi_cell(0, 4, link)
    pdf.set_text_color(0, 0, 0)

    section(pdf, "9. Jogi megjegyzés")
    body(
        pdf,
        "Ez a dokumentum DIY kutatási / prototípus célú terv. Nem minősül orvosi eszköznek, "
        "nem rendelkezik CE/FDA tanúsítvánnyal. Használat saját felelősségre. Éles inzulinadagolás "
        "előtt kiterjedt tesztelés szükséges.",
    )

    pdf.output(str(OUT))
    print(f"Generated: {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
