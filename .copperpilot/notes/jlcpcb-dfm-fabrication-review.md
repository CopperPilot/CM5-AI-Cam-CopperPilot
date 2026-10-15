# JLCPCB 6-Layer DFM & Manufacturing Constraints Review Report
**Project:** Raspberry Pi Compute Module 5 AI Camera Carrier Board (`CM5-AI-Cam-CopperPilot`)  
**Design Files Reviewed:** `CM5-AI-Cam-CopperPilot.kicad_pcb`, `CM5-AI-Cam-CopperPilot.kicad_pro`, `CM5-AI-Cam-CopperPilot.kicad_dru`  
**Reference Specification:** `.copperpilot/notes/jlcpcb-6layer-rules-spec.md`  
**Target Fabrication Process:** Official JLCPCB 6-Layer Standard Process (`JLC06161H-3313`, 1.6 mm Finished Thickness)  
**Date of Audit:** October 2026  

---

## Executive Summary

A comprehensive multi-disciplinary DFM and physical design audit was performed on `CM5-AI-Cam-CopperPilot.kicad_pcb` (55.0 mm x 40.0 mm, 6 layers), its accompanying configuration `CM5-AI-Cam-CopperPilot.kicad_pro`, and custom rules `CM5-AI-Cam-CopperPilot.kicad_dru`. 

The review identified **6 critical fabrication and assembly blockers** that will cause board failure, yield loss, or assembly impossibility if submitted directly to JLCPCB:
1. **Critical Annular Ring Under-sizing:** 198 out of 322 vias (61.5%) have 0.35 mm diameter with 0.20 mm drill, yielding an annular ring of only **0.075 mm (2.95 mil)**, which violates JLCPCB's 0.10 mm (4.0 mil) mechanical drill minimum annular ring.
2. **Missing 4x M2.5 Mounting Holes & Standoff Keepout Collisions:** Zero mounting holes are drilled on the board. When standard CM4/CM5 48.0 mm x 33.0 mm standoffs are placed, standoff hardware will crush capacitor `C4` (1.85 mm from hole center) and dead-short power via `/CM5_5V` (1.22 mm from hole center) and signal via `/HDMI0_HOTPLUG` (1.06 mm from hole center).
3. **Severe Copper-to-Board-Edge Clearance Violations:** Differential trace `/HDMI0_CLK_N` on `In2.Cu` runs within **0.169 mm (6.7 mil)** of the top routed edge, and ground/power zone fills pour to within **0.150 mm** of the board boundary, violating JLCPCB's 0.30 mm routing margin and creating risk of trace clipping and inter-layer shorts.
4. **Dangerous 5V-to-GND THT Solder Bridge Hazard:** Pin 2 of 40-pin GPIO header `PI1` (`+5V`) sits only **0.330 mm** away from the grounded shield tab `S1` of `Type_C1`, violating the 1.5–2.0 mm THT-to-connector clearance rule and creating an extreme wave/hand soldering short risk.
5. **CM5 Mezzanine Component Collisions:** 54 components sit on `B.Cu` under the CM5 module. Six SOT-23-5 ICs leave only 0.05 mm vertical clearance under standard 1.5 mm DF40C connectors; through-hole header `H3` is erroneously placed on `B.Cu` (sticking out 9 mm); and THT leads from `PI1`, `H4`, `H5`, and `J2` protrude into the CM5 underside.
6. **Mask Bridge & Fine-Pitch Dam Limits:** Camera connector `J1` (0.40 mm pitch) has solder mask dams of only **0.080 mm**, sitting at the absolute limit of green mask and failing non-green masks.

---

## 1. JLCPCB 6-Layer Stackup & Global Design Rules Comparison

### 1.1 Stackup Parameter Comparison (`JLC06161H-3313` vs CAD Implementation)

| Layer | Material / Description | Target `JLC06161H-3313` Thickness | `kicad_pcb` Configured Thickness | Target $\varepsilon_r$ | Configured $\varepsilon_r$ | Compliance & DFM Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Top Mask** | Green Solder Mask | 0.010 mm (0.4 mil) | 0.010 mm | 3.80 | 3.80 | Compliant |
| **F.Cu (L1)** | Outer Copper Foil (1 oz finished) | 0.035 mm (1.4 mil) | 0.035 mm | — | — | Compliant |
| **Dielectric 1** | Prepreg 3313 (1x) | **0.0994 mm (3.9 mil)** | **0.1000 mm** | **4.05 – 4.10** | **4.50** | **Discrepancy:** $\varepsilon_r$ mismatch shifts calculated diff impedance by ~5–8%. |
| **In1.Cu (L2)** | Inner Ground Plane (0.5 oz base) | **0.0152 mm (0.6 mil)** | **0.0350 mm (1.4 mil)** | — | — | **Non-compliant:** Inner copper is modeled as 1 oz (0.035mm). JLCPCB standard is 0.5 oz (0.0152mm). |
| **Dielectric 2** | Core FR4 | **0.5500 mm (21.7 mil)** | **0.5350 mm** | 4.50 – 4.60 | 4.50 | Minor 15 µm thickness deviation. |
| **In2.Cu (L3)** | Inner High-Speed Signal (0.5 oz) | **0.0152 mm (0.6 mil)** | **0.0350 mm (1.4 mil)** | — | — | **Non-compliant:** Modeled as 1 oz instead of 0.5 oz. |
| **Dielectric 3** | Prepreg 3313 (1x) | **0.0994 mm (3.9 mil)** | **0.1000 mm** | **4.05 – 4.10** | **4.50** | $\varepsilon_r$ mismatch. |
| **In3.Cu (L4)** | Inner Split Power Plane (0.5 oz) | **0.0152 mm (0.6 mil)** | **0.0350 mm (1.4 mil)** | — | — | **Non-compliant:** Modeled as 1 oz instead of 0.5 oz. |
| **Dielectric 4** | Core FR4 | **0.5500 mm (21.7 mil)** | **0.5350 mm** | 4.50 – 4.60 | 4.50 | Minor 15 µm thickness deviation. |
| **In4.Cu (L5)** | Inner Ground Plane (0.5 oz base) | **0.0152 mm (0.6 mil)** | **0.0350 mm (1.4 mil)** | — | — | **Non-compliant:** Modeled as 1 oz instead of 0.5 oz. |
| **Dielectric 5** | Prepreg 3313 (1x) | **0.0994 mm (3.9 mil)** | **0.1000 mm** | **4.05 – 4.10** | **4.50** | $\varepsilon_r$ mismatch. |
| **B.Cu (L6)** | Outer Copper Foil (1 oz finished) | 0.035 mm (1.4 mil) | 0.035 mm | — | — | Compliant |
| **Bottom Mask**| Green Solder Mask | 0.010 mm (0.4 mil) | 0.010 mm | 3.80 | 3.80 | Compliant |
| **Total Finished**| Total Board Thickness | **1.60 mm $\pm 10\%$** | **1.60 mm** | — | — | Nominal thickness aligns. |

*Critical Stackup Finding:* All four internal layers (`In1.Cu`, `In2.Cu`, `In3.Cu`, `In4.Cu`) are defined in KiCad with `(thickness 0.035)`. JLCPCB standard multi-layer manufacturing utilizes 0.5 oz base copper (finished ~0.0152 mm) on inner layers. Specifying 1 oz inner copper requires customized fabrication, higher core etching margins, and substantial surcharges.

---

### 1.2 Global Design Rules: JLCPCB Capability vs `.kicad_pro` vs `.kicad_dru`

| Design Parameter | JLCPCB Standard Process | JLCPCB Absolute Limit | `.kicad_pro` Rule | `.kicad_dru` Custom Override | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Min Track Width** | 0.127 mm (5.0 mil) | 0.090 mm (3.54 mil) | `0.09 mm` | None | **Compliant** |
| **Min Track Clearance** | 0.127 mm (5.0 mil) | 0.090 mm (3.54 mil) | `0.10 mm` | None | **Compliant** |
| **Min Through-Hole Drill** | 0.300 mm (12.0 mil) | 0.200 mm (7.87 mil) | `0.20 mm` | None | **Compliant** |
| **Min Via Outer Diameter** | 0.500 mm (20.0 mil) | **0.400 mm (15.7 mil)** | **0.35 mm** | None | **DEFECT:** 0.35 mm via diameter violates 0.40 mm limit. |
| **Min Annular Ring** | 0.100 mm (4.0 mil) | **0.100 mm (PTH)** | **0.075 mm** | None | **DEFECT:** 0.075 mm violates 0.10 mm standard. |
| **Hole-to-Hole (PTH-PTH)** | 0.500 mm (20.0 mil) | 0.500 mm (20.0 mil) | `0.254 mm` | None | **Relaxed:** Needs custom DRC rule to enforce 0.5mm for PTH. |
| **Drill-to-Copper Clearance**| 0.300 mm (12.0 mil) | 0.254 mm (10.0 mil) | `0.15 mm` | None | **DEFECT:** 0.15 mm violates JLCPCB 0.254 mm limit. |
| **Copper to Board Edge** | 0.400–0.500 mm | **0.300 mm (12.0 mil)** | **0.15 mm** | `Pads to board edge: min 0.0mm` | **DEFECT:** 0.15 mm global rule and 0.0 mm pad override mask edge violations. |
| **Solder Mask Dam (Green)** | 0.100 mm (4.0 mil) | 0.080 mm (3.15 mil) | Not checked | `allow_soldermask_bridges_in_footprints yes` | **DEFECT:** Suppresses DRC detection of mask dam collapse. |
| **Silkscreen Line Width** | 0.180 mm (7.0 mil) | 0.150 mm (6.0 mil) | `0.15 mm` | None | **Marginal:** CAD texts use 0.12 mm. |
| **Silkscreen Text Height** | 1.000 mm (40.0 mil) | 0.800 mm (32.0 mil) | `0.80 mm` | None | **Compliant** |
| **Silkscreen to Mask Clear** | 0.200 mm (8.0 mil) | 0.150 mm (6.0 mil) | `0.15 mm` | None | **Compliant** |

---

## 2. Clearances (Trace-Trace, Trace-Pad, Pad-Pad, Copper-Edge)

### 2.1 Track Width & Routing Spacing Distribution
Across the 1688 track segments routed on the board:
* **Track Widths:**
  * 0.1500 mm (5.91 mil): 1259 segments (74.6%) — Default digital & signal routing.
  * 0.1800 mm (7.09 mil): 165 segments (9.8%) — SD card and CSI differential pairs.
  * 0.1998–0.2202 mm: 14 segments (0.8%) — Intermediate power/clock routing.
  * 0.3500 mm (13.78 mil): 173 segments (10.2%) — Secondary power rails.
  * 0.4000 mm (15.75 mil): 76 segments (4.5%) — Primary power distribution.
  * Minimum physical track width on any layer: **0.1500 mm** (Compliant with JLCPCB 0.090 mm limit).
* **Trace-to-Trace & Trace-to-Pad Clearance:**
  * Minimum trace clearance is constrained by net classes: Default (`0.12 mm`), High-Speed (`0.12 mm`), Power (`0.20 mm`).
  * Measured physical clearances between routed copper traces meet or exceed 0.120 mm everywhere on signal layers, satisfying JLCPCB's 0.090 mm multi-layer limit.

### 2.2 Pad-to-Pad Clearances Across Adjacent SMD Components
* **Passives (0402 / 0603):** Body spacing is $\ge 0.50$ mm; minimum pad copper spacing between adjacent passives is **0.360 mm** (`R35-R36`, `R8-R11`, `C21-R16`), complying with JLCPCB's 0.20 mm minimum recommendation.
* **IC to Passives:** Clearances exceed 0.70 mm (`U5`, `U6`, `U2`, `Q1`).
* **Fine-Pitch SMD Lead Clearances:**
  * `Module1` (Hirose DF40C, 200 pins): 0.40 mm pitch, 0.20 mm pad width $\implies$ **0.200 mm copper space**.
  * `U6` (onsemi FSUSB42MX, UQFN-10): 0.40 mm pitch, 0.20 mm pad width $\implies$ **0.200 mm copper space**.
  * `J1` (IMX219 Camera Connector, 30 pins): 0.40 mm pitch, 0.22 mm pad width $\implies$ **0.180 mm copper space**.

### 2.3 Copper to Board Edge Clearances (CNC Routing Hazards)
Board boundary: $X \in [21.500, 76.500]$ mm, $Y \in [25.000, 65.000]$ mm (55.0 mm x 40.0 mm with 3.0 mm corner radii).

| Copper Feature | Layer | Net | Location / Coordinates | Measured Distance to Edge | JLCPCB Standard Requirement | Defect Severity & Consequence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Track Segment** | `In2.Cu` | `/HDMI0_CLK_N` | (58.63, 25.24) to (33.94, 25.24) | **0.1694 mm (6.7 mil)** | $\ge 0.300$ mm (routed edge) | **CRITICAL:** CNC milling bit ($\pm 0.20$ mm tolerance) will clip or sever the high-speed HDMI clock pair. |
| **Track Segment** | `B.Cu` | `GND` | (53.31, 64.56) | 0.3642 mm (14.3 mil) | $\ge 0.300$ mm | Acceptable, but below 0.50 mm recommendation. |
| **Track Segment** | `In4.Cu` | `/HDMI0_SCL` | (36.78, 25.45) to (30.94, 25.45) | 0.3766 mm (14.8 mil) | $\ge 0.300$ mm | Acceptable. |
| **Via Pad** | All Cu | `GND` | (53.31, 64.56), size 0.35mm | **0.2642 mm (10.4 mil)** | $\ge 0.300$ mm | **DEFECT:** Via copper encroaches into the 0.30 mm router margin. |
| **Via Pad** | All Cu | `/GPIO14` | (52.03, 64.53), size 0.35mm | **0.2909 mm (11.5 mil)** | $\ge 0.300$ mm | **DEFECT:** Signal via encroaches into router margin. |
| **Copper Zone Fills** | `In1.Cu` / `In4.Cu` | `GND` | Along $X = 76.35$ and $Y = 25.15$ | **0.1505 mm (5.9 mil)** | $\ge 0.300$ mm (inner planes) | **CRITICAL:** Plane copper exposed on board edge; causes copper burrs, fraying, and edge shorts. |
| **Copper Zone Fills** | `In3.Cu` | `/CM5_5V`, `/PWR_3V3` | Along $X = 76.35$ mm | **0.1505 mm (5.9 mil)** | $\ge 0.300$ mm (inner planes) | **CRITICAL:** 5V and 3.3V power planes exposed at routed edge. |

---

## 3. Via Diameters, Drill Sizes & Annular Rings

### 3.1 Via Distribution and Annular Ring Audit

| Via Outer Diameter | Drill Hole Diameter | Calculated Annular Ring | Quantity on Board | Percentage of Vias | JLCPCB Process Classification | DFM Risk Assessment |
| :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **0.350 mm (13.8 mil)** | **0.200 mm (7.9 mil)** | **0.0750 mm (2.95 mil)** | **198** | **61.49%** | **Sub-standard / Under-sized** | **CRITICAL FAILURE:** Below JLCPCB 0.10 mm mechanical drill limit. Mechanical drill registration wander ($\pm 0.05$ to $0.075$ mm) causes drill breakout and open vias. |
| 0.400 mm (15.7 mil) | 0.200 mm (7.9 mil) | 0.1000 mm (3.94 mil) | 66 | 20.50% | JLCPCB Standard Threshold | Compliant with minimum 0.10 mm annular ring. |
| 0.450 mm (17.7 mil) | 0.200 mm (7.9 mil) | 0.1250 mm (4.92 mil) | 19 | 5.90% | Standard DFM Target | Excellent manufacturing yield. |
| 0.450 mm (17.7 mil) | 0.250 mm (9.8 mil) | 0.1000 mm (3.94 mil) | 4 | 1.24% | Standard DFM Target | Compliant. |
| 0.500 mm (19.7 mil) | 0.250 mm (9.8 mil) | 0.1250 mm (4.92 mil) | 35 | 10.87% | High-Reliability Power Via | Compliant. |
| **Total Vias** | — | — | **322** | **100.0%** | — | **61.5% non-compliant annular rings** |

### 3.2 Root Cause in CAD Configuration
In `CM5-AI-Cam-CopperPilot.kicad_pro`, the board constraint was configured as:
```json
"min_via_diameter": 0.35,
"min_through_hole_diameter": 0.20,
"min_via_annular_width": 0.075
```
This allowed the autorouter and manual layout to place 198 vias with $0.075$ mm annular rings without triggering a KiCad DRC error. For JLCPCB, `min_via_diameter` must be $\ge 0.40$ mm (for 0.20 mm drill) or $\ge 0.45$ mm (recommended), and `min_via_annular_width` must be set to `0.10 mm`.

---

## 4. Silkscreen Typography & Solder Mask Dams

### 4.1 Silkscreen Typography Audit
* **Line Thickness (Stroke):**
  * JLCPCB Minimum: **0.150 mm (6.0 mil)**. Recommended: 0.18–0.20 mm.
  * Board Status: All 90 footprint Reference properties use **0.120 mm** line thickness. Visible text on `J1` (`0.12 mm`) triggers KiCad `[text_thickness]` DRC warnings. Text $< 0.15$ mm will wash out or break during screen printing.
* **Text Height:**
  * JLCPCB Minimum: **0.800 mm (32 mil)**.
  * Board Status: All footprint Reference designators use 0.80 mm x 0.80 mm (Compliant).
* **The LCSC Silkscreen Defect (398 DRC Warnings):**
  * All 90 footprints include visible `LCSC` part numbers (`C25900`, `C3020560`, etc.) placed at `(0, 0)` with height 1.27 mm.
  * Generates 199 `silk_over_copper` warnings (text covering solder pads) and 199 `silk_overlap` warnings (colliding across components).
  * 54 bottom footprints on `B.SilkS` lack `(justify mirror)` (`[nonmirrored_text_on_back_layer]`).
  * *Remediation:* Set `(hide yes)` on all 90 `LCSC` properties.
* **Silkscreen Edge Clipping (18 Warnings):**
  * `DSI1` sits 0.03 mm from the top board edge (violating 0.15 mm edge clearance).
  * `Module1` boundary silkscreen on `B.SilkS` overlaps Edge.Cuts at 8 points.
  * `HDMI1` silkscreen segments cross Edge.Cuts corner arcs.

### 4.2 Solder Mask Dams & Fine-Pitch Component Openings
* **Configured Mask Clearance:** `pad_to_mask_clearance = 0.00 mm`. Standard JLCPCB CAM applies $0.038$–$0.050$ mm auto-expansion.
* **Fine-Pitch Solder Mask Bridge Analysis:**

| Component | Package / Pitch | Pad Width | Copper Spacing | Solder Mask Dam (0.05mm expansion) | JLCPCB Minimum Dam Limit | Risk Classification |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **J1** (Camera Connector) | 30-pin FPC, 0.40 mm pitch | 0.22 mm | 0.18 mm | **0.080 mm (3.15 mil)** | 0.080 mm (Green) / 0.100 mm (Colors) | **HIGH RISK:** Sits exactly at green mask limit. Any misregistration results in stripped webs and bridged pins. |
| **U6** (USB Multiplexer) | UQFN-10, 0.40 mm pitch | 0.20 mm | 0.20 mm | **0.100 mm (3.94 mil)** | 0.080 mm (Green) / 0.100 mm (Colors) | Moderate Risk. Stencil aperture reduction required. |
| **Module1** (CM5 Mezzanine) | DF40C, 0.40 mm pitch | 0.20 mm | 0.20 mm | **0.100 mm (3.94 mil)** | 0.080 mm (Green) / 0.100 mm (Colors) | Moderate Risk. 200 pins require high-precision stencil. |

*Critical Defect:* `CM5-AI-Cam-CopperPilot.kicad_pcb` sets `(allow_soldermask_bridges_in_footprints yes)`, which deliberately suppresses DRC warnings when fine-pitch pins lack solder mask dams.

---

## 5. Mechanical Keepouts, Mounting Holes & Component SMT/THT Clearances

### 5.1 4x M2.5 Mounting Holes Missing & Standoff Keepout Collisions
Standard Raspberry Pi Compute Module 4 and 5 carrier specifications mandate four M2.5 mounting holes on a **48.0 mm x 33.0 mm** grid pattern:
* **Hole 1 (Top-Left):** (24.80, 28.42) mm
* **Hole 2 (Bottom-Left):** (24.80, 61.42) mm
* **Hole 3 (Top-Right):** (72.80, 28.42) mm
* **Hole 4 (Bottom-Right):** (72.80, 61.42) mm
* **Specification:** 2.7 mm drill NPTH with **5.0 mm diameter keepout zone** (2.5 mm radius) on both sides.

#### Physical Conflict Audit at Nominal Mounting Locations:
1. **Physical Holes Absent:** **0 mounting holes exist on the board.** The carrier board cannot be mechanically fastened to the CM5 module or carrier frame.
2. **Hole 4 (Bottom-Right, 72.80, 61.42) — CRITICAL HARD CONFLICT:**
   * **Capacitor `C4` (10 µF, 0805 on `B.Cu`):** Placed at (71.00, 61.00), only **1.85 mm** from hole center. An 0805 body extends $\pm 1.0$ mm, placing it directly under a 5.0 mm standoff or screw head. Fastener torque will crush `C4`.
   * **Power Via `/CM5_5V`:** Placed at (71.94, 62.28), only **1.22 mm** from hole center. Fastener hardware will bite into the via barrel, dead-shorting the main 5V system supply to ground/chassis.
3. **Hole 1 (Top-Left, 24.80, 28.42) — SEVERE CONFLICT:**
   * **Signal Via `/HDMI0_HOTPLUG`:** Placed at (24.31, 29.36), only **1.06 mm** from hole center. Direct fastener crush/short risk.
   * Signal Vias `/HDMI0_SDA` (2.96 mm) and `/HDMI_5V` (2.83 mm) sit on the margin of a 6.0 mm standoff keepout.

---

### 5.2 Component Clearance Hazards (PI1 Pin 2 to Type_C1 Shield Tab)
* **Components:** `PI1` (40-Pin GPIO Header, 2.54 mm pitch THT) and `Type_C1` (GCT USB4105 16-Pin USB-C Receptacle).
* **Geometry:**
  * `PI1.2` is a 1.70 mm circular through-hole pad centered at (25.00, 58.315) mm, carrying net `+5V`.
  * `Type_C1.S1` is a $1.00 \times 2.10$ mm oval through-hole shield tab centered at (26.68, 59.395) mm, carrying net `GND`.
* **Measured Clearance:**
  * Center-to-center distance: 2.00 mm.
  * Pad edge-to-edge copper clearance: **0.330 mm (13.0 mil)**.
  * Courtyard boundary clearance: **0.195 mm**.
* **DFM Hazard:**
  * Standard IPC-2221 and JLCPCB assembly rules require $\ge 1.50$–$2.00$ mm between wave/selective soldering points and adjacent metal shells.
  * A 0.330 mm gap between a raw 5V primary power pin and a grounded connector shield tab will create an unavoidable solder bridge during wave or selective soldering, resulting in a dead short from 5V to GND.

---

### 5.3 CM5 Mezzanine Interface Underside Clearance (B.Cu)
* **Underside Component Population:** 54 components are placed on `B.Cu` within the envelope of the CM5 module.
* **Vertical Clearance Crisis:**
  * Standard Hirose `DF40C-100DS-0.4V` receptacle provides a mated stack height of **1.50 mm**.
  * Six SOT-23-5 ICs (`U1`, `U2`, `U3`, `U4`, `U7`, `U8`) have a maximum component body height of **1.45 mm**.
  * Remaining vertical headroom: $1.50 - 1.45 = \mathbf{0.05\ \text{mm}}$ (50 µm). Any solder paste fillet or board warpage causes mechanical collision with the CM5 module underside.
* **Through-Hole Lead Protrusions:**
  * Through-hole pin header `H3` (`CM5:PinHeader_1x03_P2.54mm_Vertical`) is placed directly on `B.Cu` at (67.00, 49.54). Pin header tails stick out 8.5–11.5 mm, creating an impossible mechanical collision.
  * THT pin tails from `PI1` (40 pins), `H4` (3 pins), `H5` (3 pins), and `J2` (7 pins) protrude 1.5–2.5 mm through `B.Cu`, shorting directly into the CM5 ground shield.
* **Remediation:**
  1. Specify `DF40HC(3.0)-100DS-0.4V` (3.0 mm stack height) in the BOM.
  2. Move `H3` from `B.Cu` to `F.Cu`.
  3. Require flush lead trimming ($\le 0.5$ mm) and secondary Kapton insulation over THT pin fields.

---

### 5.4 Courtyard Integrity
* **Missing Courtyard on `HDMI1`:** `HDMI1` (`Molex_47151-0001`) completely lacks an `F.CrtYd` layer definition. It physically collides with `DSI1` by 5.63 mm in bounding box projection.

---

## 6. Comprehensive Remediation Action Checklist

1. [ ] **Fix Via Annular Rings:** Batch-update all 198 vias from diameter 0.35 mm / drill 0.20 mm to **diameter 0.40 mm / drill 0.20 mm** (min 0.10 mm annular ring) or **diameter 0.45 mm / drill 0.20 mm** (preferred DFM).
2. [ ] **Update `.kicad_pro` Rules:**
   * Change `min_via_diameter` to `0.40 mm`.
   * Change `min_via_annular_width` to `0.10 mm`.
   * Change `min_copper_edge_clearance` to `0.30 mm` (or `0.50 mm`).
   * Change `min_hole_clearance` to `0.254 mm`.
   * Remove custom `.kicad_dru` override `(rule "Pads to board edge" (constraint edge_clearance (min 0.0mm)))`.
3. [ ] **Pull Back Copper from Board Edges:**
   * Reroute `/HDMI0_CLK_N` on `In2.Cu` at (58.63, 25.24) to maintain $\ge 0.50$ mm clearance from $Y = 25.0$ mm.
   * Reroute edge vias at (53.31, 64.56) and (52.03, 64.53) to $\ge 0.50$ mm from $Y = 65.0$ mm.
   * Set zone clearance to board edge to $0.40$ mm across all internal planes.
4. [ ] **Drill 4x M2.5 Mounting Holes & Clear Keepouts:**
   * Add 4x `Mounting_Hole_M2.5` (2.7 mm NPTH, 5.0 mm keepout) at (24.8, 28.42), (72.8, 28.42), (24.8, 61.42), and (72.8, 61.42).
   * Relocate capacitor `C4` away from (71.0, 61.0) to outside the 5.0 mm circle.
   * Relocate `/CM5_5V` via at (71.94, 62.28) and `/HDMI0_HOTPLUG` via at (24.31, 29.36).
5. [ ] **Resolve PI1 to Type_C1 Solder Bridge Hazard:**
   * Shift `Type_C1` +1.0 mm in +X or adjust `PI1` position to achieve $\ge 1.50$ mm copper clearance between `PI1.2` (5V) and `Type_C1.S1` (GND).
6. [ ] **Sanitize Silkscreen:**
   * Set `(hide yes)` on all 90 `LCSC` properties.
   * Increase all visible silkscreen text line thicknesses to $\ge 0.15$ mm.
   * Trim `DSI1` and `HDMI1` silkscreen lines $\ge 0.15$ mm away from board edges and pads.
7. [ ] **Resolve CM5 Underside Mechanical Conflicts:**
   * Move `H3` from `B.Cu` to `F.Cu`.
   * Update mezzanine connector BOM to `DF40HC(3.0)-100DS-0.4V` (3.0 mm mating height).
8. [ ] **Fix Inner Copper Stackup:** Update `CM5-AI-Cam-CopperPilot.kicad_pcb` inner layers `In1.Cu`–`In4.Cu` thickness from `0.035 mm` to `0.0152 mm` (0.5 oz) and prepreg $\varepsilon_r$ to `4.05`.
