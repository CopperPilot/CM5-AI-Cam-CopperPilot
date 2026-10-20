# JLCPCB Manufacturing Order Specification

**Project:** CM5 AI Camera Carrier Board  
**Target Fabricator:** JLCPCB (Shenzhen JLC Electronics Co., Ltd.)  
**Service Type:** PCB Fabrication & Standard PCBA (Turnkey Assembly)  
**Date:** 2026-10-17  
**Validation Status:** 0 ERC / 0 DRC / 100% Schematic Parity Verified  

---

## 1. PCB Fabrication Specification

| Order Parameter | Value | Notes |
|---|---|---|
| **Base Material** | FR-4 Standard (Tg 155°C) | High-speed multi-layer FR4 |
| **Layer Count** | 6 Layers | 1x Top, 4x Internal, 1x Bottom |
| **Board Dimensions** | 55.0 mm × 40.0 mm | Raspberry Pi CM5 form factor |
| **Board Thickness** | 1.6 mm ±10% | Matches JLC standard 6-layer build |
| **Outer Copper Weight** | 1 oz (35 µm) | Top (F.Cu) & Bottom (B.Cu) |
| **Inner Copper Weight** | 0.5 oz (15.2 µm) | In1.Cu, In2.Cu, In3.Cu, In4.Cu |
| **Surface Finish** | ENIG (Electroless Nickel Immersion Gold) | Gold thickness ≥ 1 µ" (0.025 µm), Ni ≥ 100 µ" |
| **Solder Mask Colour** | Green | Standard gloss green LDI |
| **Silkscreen Colour** | White | High-contrast LDI white |
| **Edge Connector / Bevel** | None | No gold fingers |
| **Castellated Holes** | None | Standard routed perimeter |
| **Via Process** | Tented (LPI Solder Mask Covered) | All vias tented both sides |
| **Minimum Track / Space** | 0.127 mm / 0.095 mm (0.127 mm 100 Ω diff; 0.150 mm general) | Meets JLC 0.09 mm capability with high yield |
| **Minimum Hole Size / Drill** | 0.20 mm drill / 0.40 mm pad | Standard multilayer micro-via capability (hole-to-hole ≥ 0.254 mm) |
| **Impedance Control** | Yes (Controlled Stackup) | **100 Ω diff (MIPI CSI-2, MIPI DSI, HDMI TMDS), 90 Ω diff (USB 2.0), 50 Ω single-ended** |
| **JLC Stackup Code** | **JLC06161H-7628** | Standard 6-layer controlled-impedance stackup (compatible with `JLC06161H-3313`) |
| **PCB Delivery Format** | Single Board | Perimeter CNC routed with 3 mm corner radiuses |

---

## 2. Controlled Impedance Stackup (JLC06161H-7628)

| Layer # | Layer Name | Material | Thickness | Copper Weight | Function |
|---|---|---|---|---|---|
| 1 | **F.Cu (Top)** | Copper | 0.0350 mm | 1.0 oz | Top SMT components, high-speed microstrip escapes, power stages |
| - | Dielectric 1 | 7628 Prepreg | 0.2104 mm | - | Dielectric ($\varepsilon_r = 4.6$) |
| 2 | **In1.Cu** | Copper | 0.0152 mm | 0.5 oz | Primary Ground Plane (`GND` zone) & inner escape routing |
| - | Dielectric 2 | FR4 Core | 0.4000 mm | - | Core Dielectric ($\varepsilon_r = 4.6$) |
| 3 | **In2.Cu** | Copper | 0.0152 mm | 0.5 oz | High-Speed Signal Routing (`HDMI0`, `DSI1`, peripheral signals) |
| - | Dielectric 3 | 7628 Prepreg | 0.2104 mm | - | Dielectric ($\varepsilon_r = 4.6$) |
| 4 | **In3.Cu** | Copper | 0.0152 mm | 0.5 oz | Power Distribution Zones (`/PWR_3V3`, `/CM5_5V`) & inner routing |
| - | Dielectric 4 | FR4 Core | 0.4000 mm | - | Core Dielectric ($\varepsilon_r = 4.6$) |
| 5 | **In4.Cu** | Copper | 0.0152 mm | 0.5 oz | Secondary Ground Plane (`GND` zone) & high-speed routing |
| - | Dielectric 5 | 7628 Prepreg | 0.2104 mm | - | Dielectric ($\varepsilon_r = 4.6$) |
| 6 | **B.Cu (Bottom)** | Copper | 0.0350 mm | 1.0 oz | CM5 Mezzanine (`Module1`), LDOs (`U1–U3`), USB Mux (`U6`), switches |

### 2.1 Controlled Impedance Netclass & Trace Geometry Table

| Netclass (`CM5-AI-Cam-CopperPilot.kicad_pro`) | Target Impedance | Interfaces & Net Patterns | Trace Width ($W$) | Differential Gap ($S$) | Calculated $Z_{\text{diff}}$ / $Z_0$ (`JLC06161H-7628` Stripline) | Calculated $Z_{\text{diff}}$ / $Z_0$ (`JLC06161H-3313` Microstrip) |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **`HighSpeed_100R`** | **100 Ω ±10% Diff** | MIPI CSI-2 (`/CAM0_*`, `/CSI_*`), MIPI DSI (`/DSI1_*`), HDMI TMDS (`/HDMI0_CLK_*`, `/HDMI0_TX*`) | **0.127 mm** | **0.150 mm** | **100.1 Ω** | **98.3 Ω** |
| **`HighSpeed_90R`** | **90 Ω ±10% Diff** | USB 2.0 Hi-Speed (`/USB0_P/N`, `/USB0_B_*`, `/USBB_*`, `/USBD0_*`) | **0.180 mm** | **0.150 mm** | **89.6 Ω** | **88.7 Ω** |
| **Single-Ended 50 Ω** | **50 Ω ±10% SE** | Camera MCLK & SDIO Clocks (`/MCLK`, `/X1_OUT`, `/SD_CLK`, `/SD_CMD`, `/SD_DAT0..3`) | **0.180 mm** | — | **53.7 Ω** | **47.0 Ω** |

---

## 3. SMT Assembly (PCBA) Specification

| Assembly Parameter | Value | Notes |
|---|---|---|
| **Assembly Tier** | Standard PCBA | High-precision SMT pick & place |
| **Assembly Sides** | Both Sides (Top & Bottom) | Top: USB-C, HDMI, Camera, Buck, Inductors; Bottom: CM5 sockets, LDOs, USB mux, switches |
| **Tooling / Rails** | Added by JLCPCB | Fabricator adds temporary edge process rails with fiducials |
| **Component Count** | 87 Populated Components (90 Total Footprints) | 42 Unique BOM Lines (`R31, R32, R33` DNP straps excluded) |
| **BOM Sourcing** | 100% LCSC Pre-Sourced | All 42 BOM lines have verified LCSC Part Numbers (`C25803`, `C47773`, `C15075`, `C2960187`, `C424662`, `C110443`, `C32949`, `C1534`) |
| **Lead-Free RoHS** | Yes (RoHS Compliant) | SAC305 lead-free reflow profile |
| **Conformal Coating** | No | Standard clean post-reflow |
| **DNP Components** | 3 DNP (`R31`, `R32`, `R33`) | Excluded from `bom_jlcpcb.csv` and `cpl_jlcpcb.csv` so `WL_nDisable`, `BT_nDisable`, and `USB_OTG_ID` are not grounded |
| **Order Number Location** | Specify location | Fabricator-placed on bottom silkscreen under CM5 module |

---

## 4. Production Deliverables Checklist

- [x] **Gerber Files:** RS-274X format in `jlcpcb_production/gerbers/` (13 Gerber layer files + 2 Excellon drill files + drill report + job file = 17 files)
- [x] **Drill Files:** Excellon decimal drill files (PTH + NPTH separate)
- [x] **Bill of Materials:** `jlcpcb_production/assembly/bom_jlcpcb.csv` with Comment, Designator, Footprint, LCSC (DNP excluded)
- [x] **Centroid / CPL:** `jlcpcb_production/assembly/cpl_jlcpcb.csv` with Ref, Val, Package, PosX, PosY, Rot, Side (DNP excluded)
- [x] **IPC-D-356 Netlist:** `jlcpcb_production/netlist/CM5-AI-Cam-CopperPilot.d356`
- [x] **Archive Package:** `jlcpcb_production/gerbers_jlcpcb.zip`
