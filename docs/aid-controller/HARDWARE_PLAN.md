# AID Pendant Controller — Hardware Plan

**Workstream:** `aid-controller`  
**Date:** 2026-07-11  
**PDF:** [AID_Pendant_Controller_Hardware_Plan.pdf](./AID_Pendant_Controller_Hardware_Plan.pdf)

## Recommendation

Use **nRF52840** (not ESP32-C6 AMOLED) for smallest size, best BLE stability, and lowest 24/7 power.

| Phase | Hardware |
|-------|----------|
| Prototype | Seeed XIAO nRF52840 |
| Production | Insight SIP ISP1807-LR on custom Ø32 mm round PCB |

## Target dimensions

- **Ø35 mm × 7.5 mm** enclosure
- **~12–15 g** (without chain)
- **2–4 days** battery (225–300 mAh, display sleep)

## BOM summary

See PDF section 2 for full list with procurement links and manufacturer photos in `images/`.

## Images (manufacturer sources)

| File | Component |
|------|-----------|
| `images/isp1807-lr.png` | Insight SIP ISP1807-LR |
| `images/xiao-nrf52840.jpg` | Seeed XIAO nRF52840 |
| `images/blyst840.jpg` | I-SYST BLYST840 (alt module) |
| `images/round-lipo.jpg` | Round LiPo 353027/363027 |
| `images/oled042.jpg` | 0.42" OLED module |
| `images/round-oled075.jpg` | Optional 0.75" round OLED |

## Lifestyle renders (final model)

Photorealistic concept images of the Ø35 mm pendant (AI-generated visualization):

| Image | Scene |
|-------|-------|
| `lifestyle/aid-pendant-lifestyle-neck.png` | Worn on necklace |
| `lifestyle/aid-pendant-lifestyle-palm.png` | Scale in palm |
| `lifestyle/aid-pendant-lifestyle-charging.png` | Nightstand magnetic charging |

## Regenerate PDF

```bash
cd docs/aid-controller && python3 generate_pdf.py
```
