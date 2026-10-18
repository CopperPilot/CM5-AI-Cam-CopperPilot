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
| **Minimum Track / Space** | 0.150 mm / 0.150 mm (0.127 mm fine escapes) | Meets JLC 0.09 mm capability with high yield |
| **Minimum Hole Size / Drill** | 0.20 mm drill / 0.40 mm pad | Standard multilayer micro-via capability |
| **Impedance Control** | Yes (Controlled Stackup) | 90 Ω diff (USB/MIPI/HDMI), 50 Ω single-ended |
| **JLC Stackup Code** | **JLC06161H-7628** | Standard 6-layer high-yield stackup |
| **PCB Delivery Format** | Single Board | Perimeter CNC routed with 3 mm corner radiuses |

---

## 2. Controlled Impedance Stackup (JLC06161H-7628)

| Layer # | Layer Name | Material | Thickness | Copper Weight | Function |
|---|---|---|---|---|---|
| 1 | **F.Cu (Top)** | Copper | 0.035 mm | 1.0 oz | Components, RF/High-speed escapes, Power |
| - | Dielectric 1 | 7628 Prepreg | 0.2104 mm | - | Dielectric (εr = 4.6) |
| 2 | **In1.Cu** | Copper | 0.0152 mm | 0.5 oz | Solid Ground Plane (Return for Top & In2) |
| - | Dielectric 2 | FR4 Core | 0.4000 mm | - | Core Dielectric (εr = 4.6) |
| 3 | **In2.Cu** | Copper | 0.0152 mm | 0.5 oz | High-Speed Signal Routing (HDMI, CSI, DSI) |
| - | Dielectric 3 | 7628 Prepreg | 0.2104 mm | - | Dielectric (εr = 4.6) |
| 4 | **In3.Cu** | Copper | 0.0152 mm | 0.5 oz | Solid Ground Plane (Return for In2 & In4) |
| - | Dielectric 4 | FR4 Core | 0.4000 mm | - | Core Dielectric (εr = 4.6) |
| 5 | **In4.Cu** | Copper | 0.0152 mm | 0.5 oz | Power Rails & Peripheral Signal Routing |
| - | Dielectric 5 | 7628 Prepreg | 0.2104 mm | - | Dielectric (εr = 4.6) |
| 6 | **B.Cu (Bottom)** | Copper | 0.035 mm | 1.0 oz | Components, Decoupling & Ground Pour |

---

## 3. SMT Assembly (PCBA) Specification

| Assembly Parameter | Value | Notes |
|---|---|---|
| **Assembly Tier** | Standard PCBA | High-precision SMT pick & place |
| **Assembly Sides** | Both Sides (Top & Bottom) | Top: CM5 sockets, USB, inductors; Bottom: LDOs, SD, switches |
| **Tooling / Rails** | Added by JLCPCB | Fabricator adds temporary edge process rails with fiducials |
| **Component Count** | 90 Total Placed Components | 42 Unique BOM Lines |
| **BOM Sourcing** | 100% LCSC Pre-Sourced | All 42 BOM lines have verified in-stock LCSC Part Numbers |
| **Lead-Free RoHS** | Yes (RoHS Compliant) | SAC305 lead-free reflow profile |
| **Conformal Coating** | No | Standard clean post-reflow |
| **DNP Components** | 0 DNP | All parts on board are populated for 100% functional carrier |
| **Order Number Location** | Specify location | Bottom silkscreen `JLCJLCJLCJLC` placeholder or under CM5 module |

---

## 4. Production Deliverables Checklist

- [x] **Gerber Files:** RS-274X format in `jlcpcb_production/gerbers/` (12 layer files)
- [x] **Drill Files:** Excellon decimal drill files (PTH + NPTH separate)
- [x] **Bill of Materials:** `jlcpcb_production/assembly/bom_jlcpcb.csv` with Comment, Designator, Footprint, LCSC Part #
- [x] **Centroid / CPL:** `jlcpcb_production/assembly/cpl_jlcpcb.csv` with Designator, Mid X, Mid Y, Layer, Rotation
- [x] **IPC-D-356 Netlist:** `jlcpcb_production/netlist/CM5-AI-Cam-CopperPilot.d356`
- [x] **Archive Package:** `jlcpcb_production/gerbers_jlcpcb.zip`
