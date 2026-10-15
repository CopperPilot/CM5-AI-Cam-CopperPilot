# Component Placement, Physical Spacing, and Assembly Clearance Survey
**Board:** `CM5-AI-Cam-CopperPilot.kicad_pcb` (55.0 mm x 40.0 mm, 6-Layer)  
**Target Process:** JLCPCB Standard Multi-layer PCB Fabrication & Double-Sided PCBA (SMT)  
**Analysis Date:** October 2026  

---

## 1. Executive Summary

This survey evaluates the component placement density, physical clearances, courtyard definitions, solder mask integrity, and mechanical keepouts across the 55.0 mm x 40.0 mm carrier board (`CM5-AI-Cam-CopperPilot.kicad_pcb`). The design accommodates 90 footprints across both layers (36 on Top `F.Cu`, 54 on Bottom `B.Cu`).

### Key Assessment Findings
1. **Critical Mechanical Defect — 4x M2.5 Mounting Holes Missing:** No mounting holes are defined or drilled anywhere on the board (NPTH count is 2 for alignment pegs; 0 mounting holes). Placing standard Raspberry Pi CM4/CM5 48.0 mm x 33.0 mm standoffs will crush capacitor `C4` (located 1.85 mm from the bottom-right hole center) and short out power via `/CM5_5V` (1.22 mm away) and `/HDMI0_HOTPLUG` (1.06 mm away).
2. **Critical Mechanical Defect — Through-Hole Header H3 on Mating Side (`B.Cu`):** `H3` (`PinHeader_1x03_P2.54mm_Vertical`) is placed directly on `B.Cu` at (67.00, 49.54). Standard 2.54 mm pin headers stick out 8.5–11.5 mm, creating a hard physical collision with the plugged-in Compute Module 5.
3. **Severe Height Constraint Under CM5 Module:** With 54 components placed on `B.Cu`, six SOT-23-5 regulators/switches (`U1`, `U2`, `U3`, `U4`, `U7`, `U8`) have a package height of 1.45 mm. If standard Hirose DF40C-100DS-0.4V connectors (1.5 mm mating height) are assembled, nominal vertical clearance to the CM5 underside is only 0.05 mm (50 µm), violating standard CM4/CM5 carrier guidelines ($\le 1.2$ mm). Tall mezzanine variants (DF40HC 3.0 mm) must be specified.
4. **Through-Hole Lead Protrusions Under CM5:** THT connectors on `F.Cu` (`PI1` 40-pin GPIO, `H4`, `H5`, and `J2` vertical USB-A) have pin tails protruding 1.5–2.5 mm through `B.Cu`, directly into the CM5 module's ground shield and bottom surface.
5. **Fine-Pitch Solder Bridge Risks:** 0.4 mm pitch SMD components—`U6` (UQFN-10), `J1` (IMX219 camera connector, 30-pin), and `Module1` (2x 100-pin Hirose DF40C)—have copper pad-to-pad gaps of 0.18–0.20 mm. Solder mask dams between pins are only 0.08–0.10 mm, right at or below the standard JLCPCB minimum green solder mask web limit (0.10 mm), creating significant solder bridging risks unless CAM gang-masking or advanced dry-film mask is applied.
6. **Courtyard Anomalies:** Footprint `HDMI1` (`Molex_47151-0001`) completely lacks a courtyard definition (`F.CrtYd`), causing a 5.63 mm 2D bounding box collision with adjacent `DSI1` display connector.

---

## 2. High-Density & Tight Component Clusters

### 2.1 Buck Regulator U5 Cluster (`F.Cu`)
The switching regulator `U5` (MPS MP1658GTF-Z, TSOT-23-6) operates with inductor `L7` (Bourns SRP5030CC 4.7 µH), high-frequency bypass caps (`C20`, `C21`, `C24`), bulk caps (`C22`), and feedback/bootstrap resistors (`R10`, `R16`, `R19`, `R20`, `R21`).

| Component Pair | Types | Center Dist (mm) | Courtyard Clear (mm) | Min Pad-to-Pad (mm) | JLCPCB SMT Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **U5 — R19** | TSOT-23-6 — 0402 | 2.91 | 0.343 | 0.743 | Acceptable (adequate rework access) |
| **U5 — C21** | TSOT-23-6 — 0402 | 3.23 | 0.410 | 1.010 | Acceptable |
| **U5 — R16** | TSOT-23-6 — 0402 | 3.05 | 0.420 | 1.020 | Acceptable |
| **U5 — X1** | TSOT-23-6 — 3225 OSC | 5.32 | 0.600 | 1.450 | Acceptable |
| **U5 — L7** | TSOT-23-6 — SRP5030 Inductor | 7.26 | 1.463 | 3.562 | Good thermal isolation |
| **C21 — R16** | 0402 — 0402 | 1.00 | **0.070** | 0.370 | Tight courtyard; pad clearance ok |
| **C24 — R20** | 0402 — 0402 | 1.00 | **0.070** | 0.370 | Tight courtyard; pad clearance ok |
| **R19 — L7** | 0402 — SRP5030 Inductor | 4.61 | **0.180** | 2.180 | Tight to inductor body keepout |
| **C20 — R10** | 0402 — 0402 | 2.53 | 0.690 | 0.990 | Ample clearance |
| **R20 — R21** | 0402 — 0402 | 3.16 | 2.060 | 2.360 | Ample clearance |

*Observations:* The 0402 passive pairs (`C21-R16`, `C24-R20`) are placed side-by-side with 1.00 mm center pitch. Their physical body spacing is 0.50 mm (exceeding JLCPCB's 0.20 mm limit), but the KiCad IPC-7351 nominal courtyards have only 0.07 mm clearance between their boundary lines.

---

### 2.2 USB Multiplexer U6 Cluster (`B.Cu`)
`U6` is an onsemi FSUSB42MX analog multiplexer in an ultra-compact 10-lead UQFN package (1.4 mm x 1.8 mm, 0.40 mm lead pitch) on `B.Cu` at (29.50, 35.00). It switches D+/D- lines between the CM5 module, USB-A host port, and external interfaces, surrounded by 0R strapping resistors (`R1`, `R22`, `R24`, `R28`, `R29`, `R31`, `R32`, `R33`) and decoupling capacitor `C28`.

| Component Pair | Types | Center Dist (mm) | Courtyard Clear (mm) | Min Pad-to-Pad (mm) | JLCPCB SMT Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **U6 — R1** | UQFN-10 — 0402 | 3.04 | 0.570 | 0.970 | Acceptable |
| **U6 — R24** | UQFN-10 — 0402 | 3.16 | 1.230 | 1.630 | Acceptable |
| **U6 — R28** | UQFN-10 — 0402 | 3.16 | 1.230 | 1.630 | Acceptable |
| **U6 — C28** | UQFN-10 — 0402 | 3.50 | 1.090 | 1.490 | Acceptable |
| **U6 — R33** | UQFN-10 — 0402 | 4.24 | 1.356 | 2.386 | Acceptable |
| **R22 — R24** | 0402 — 0402 | 2.00 | **0.140** | 0.440 | Tight courtyard; pad clearance ok |
| **R24 — R28** | 0402 — 0402 | 2.00 | **0.140** | 0.440 | Tight courtyard; pad clearance ok |
| **R28 — R33** | 0402 — 0402 | 2.00 | **0.140** | 0.440 | Tight courtyard; pad clearance ok |
| **R1 — R29** | 0402 — 0402 | 3.00 | 2.060 | 2.360 | Ample clearance |
| **R29 — R31** | 0402 — 0402 | 2.00 | 1.060 | 1.360 | Ample clearance |
| **R31 — R32** | 0402 — 0402 | 2.00 | 1.060 | 1.360 | Ample clearance |

*Observations:* Spacing around `U6` is well controlled ($> 0.5$ mm from IC body to passives). Resistors `R22`, `R24`, `R28`, `R33` form an end-to-end passive bank along X = 26.50 mm spaced at 2.0 mm intervals in Y, maintaining 0.44 mm pad-to-pad clearance.

---

### 2.3 Level Shifters Q1 / Q2 Cluster (`B.Cu`)
Dual discrete N-channel MOSFET level shifters `Q1` and `Q2` (Diodes Inc DMG1012T, Texas DRT-3 / SOT-523 package) translate I2C and control signals between 1.8V and 3.3V domains on `B.Cu` at (35.50, 43.50) and (32.50, 43.50). They interface with pull-up resistors (`R4`, `R5`, `R7`, `R8`, `R11`, `R12`, `R13`) and LDO regulators `U1` and `U2`.

| Component Pair | Types | Center Dist (mm) | Courtyard Clear (mm) | Min Pad-to-Pad (mm) | JLCPCB SMT Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Q1 — Q2** | DRT-3 — DRT-3 | 3.00 | 1.400 | 2.000 | Good spacing between transistors |
| **Q1 — U2** | DRT-3 — SOT-23-5 | 3.00 | **0.150** | 0.704 | Boundary clearance; adequate pad gap |
| **Q1 — R4** | DRT-3 — 0402 | 2.50 | 0.870 | 1.145 | Acceptable |
| **Q1 — R5** | DRT-3 — 0402 | 2.50 | 0.870 | 1.145 | Acceptable |
| **Q2 — R7** | DRT-3 — 0402 | 2.50 | 0.870 | 1.145 | Acceptable |
| **Q2 — R8** | DRT-3 — 0402 | 2.50 | 0.870 | 1.145 | Acceptable |
| **R8 — R11** | 0402 — 0402 | 1.12 | **0.060** | 0.360 | Very tight courtyard (60 µm margin) |
| **R11 — R13** | 0402 — 0402 | 2.00 | 1.060 | 1.360 | Acceptable |
| **R13 — R12** | 0402 — 0402 | 4.00 | 3.060 | 3.360 | Ample clearance |

*Observations:* `R8` and `R11` are offset by 1.0 mm in X and 0.5 mm in Y (center-to-center 1.12 mm), placing their diagonal courtyards within 60 µm of each other. Pad-to-pad distance is 0.360 mm, satisfying JLCPCB's 0.20 mm pad clearance rule.

---

### 2.4 Camera Connector J1 Cluster (`F.Cu`)
`J1` (`CM5:Camera_Module_IMX219-D160`) is a 30-pin 0.4 mm pitch fine-pitch SMT connector for the Raspberry Pi Camera Module (IMX219 sensor) located at (58.71, 43.00). It is fed by three common-mode chokes (`L1`, `L2`, `L3`: Coilank ACM1210 / 0504 package) and camera passives (`C7`, `C16`, `C19`, `C27`, `R35`, `R36`).

| Component Pair | Types | Center Dist (mm) | Courtyard Clear (mm) | Min Pad-to-Pad (mm) | JLCPCB SMT Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **J1 — L1** | Camera 30P — ACM1210 Choke | 10.36 | 12.953 | 5.534 | Wide routing channel |
| **J1 — L2** | Camera 30P — ACM1210 Choke | 13.26 | 7.369 | 8.389 | Wide routing channel |
| **J1 — L3** | Camera 30P — ACM1210 Choke | 11.52 | 10.102 | 6.442 | Wide routing channel |
| **L1 — L3** | ACM1210 — ACM1210 | 3.00 | 0.940 | 1.450 | Good differential choke pitch |
| **L3 — L2** | ACM1210 — ACM1210 | 3.00 | 0.940 | 1.450 | Good differential choke pitch |
| **R35 — R36** | 0402 — 0402 | 1.00 | **0.060** | 0.360 | Very tight courtyard (60 µm margin) |
| **R36 — C27** | 0402 — 0402 | 1.00 | **0.070** | 0.370 | Tight courtyard |
| **C27 — C19** | 0402 — 0402 | 1.00 | **0.080** | 0.380 | Tight courtyard |
| **C6 — C16** | 0402 — 0402 | 1.00 | **0.080** | 0.380 | Tight courtyard |
| **C16 — C8** | 0402 — 0402 | 1.00 | **0.080** | 0.380 | Tight courtyard |

*Observations:* The common mode chokes (`L1-L3`) have ample clearance to `J1` ($> 5.5$ mm pad distance), allowing impedance-matched routing. However, the camera power decoupling capacitor bank (`C6`, `C16`, `C8`) and filter resistors (`R35`, `R36`, `C27`, `C19`) are placed on a dense 1.00 mm grid with tight 60–80 µm courtyard clearances.

---

### 2.5 Compute Module 5 (Module1) Mezzanine Footprint (`B.Cu`)
`Module1` contains two 100-pin Hirose DF40C mezzanine connectors placed on `B.Cu` at (72.80, 61.42, 90° rotation):
* **Connector 1 (Pins 1–100):** Board X in [39.90, 62.70] mm, Y in [59.99, 63.77] mm.
* **Connector 2 (Pins 101–200):** Board X in [39.90, 62.70] mm, Y in [26.07, 29.85] mm.
* **Connector Pitch & Span:** Parallel span between connectors is exactly 33.0 mm center-to-center.
* **Component Clearance to DF40 Pads:** Closest discrete component is `C30` (0402, B.Cu at 57.50, 35.50), which sits 5.65 mm away from Connector 2 pads. There is no horizontal crowding encroaching onto the DF40 SMT pads.

---

## 3. Evaluation Against JLCPCB SMT Pick-and-Place Capabilities

| Parameter | JLCPCB Standard PCBA Capability | Measured Board Range | Compliance Status | Risk & Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Min SMD Component Size** | 0402 (1005 Metric) | 0402 (SMD C & R) | **Compliant** | Standard feeder support; no 0201 parts used |
| **Passive-to-Passive Spacing** | Min 0.15 mm; Rec 0.20 mm | 0.360–0.460 mm (Pad-to-Pad) / 0.50 mm (Body) | **Compliant** | Body clearance satisfies 0.20 mm SMT rule |
| **IC-to-Passive Spacing** | Min 0.25 mm; Rec 0.30 mm | 0.704–1.020 mm (Pad-to-Pad) | **Compliant** | All ICs have $> 0.50$ mm pad spacing to passives |
| **IC-to-IC Spacing** | Min 0.50 mm; Rec 0.80 mm | 1.400 mm (`Q1-Q2`) / 3.00 mm (`Q1-U2`) | **Compliant** | Excellent physical separation |
| **Pad-to-Pad Copper Clearance** | Min 0.127 mm (5.0 mil) | Min 0.360 mm (between distinct passives) | **Compliant** | Ample copper clearance between adjacent parts |
| **Fine-Pitch SMT Lead Pitch** | Min 0.35 mm | 0.40 mm (`U6`, `J1`, `Module1`) | **Marginal / High Risk** | 0.4 mm pitch requires high-accuracy stencil |
| **Solder Mask Dam (Green)** | Min 0.08 mm; Rec 0.10 mm | **0.080 mm** (`J1`), **0.100 mm** (`U6`, `Module1`) | **High Risk** | `J1` dam (0.08 mm) is at absolute fabrication limit |
| **Solder Mask Clearance Setting** | 0.00 mm (CAD) | `(pad_to_mask_clearance 0)` | **Caution** | Relies on JLCPCB CAM to auto-expand mask |
| **Mask Bridges in Footprints** | Disallow for fine pitch | `allow_soldermask_bridges_in_footprints yes` | **Defect** | Suppresses DRC warnings for bridged pads |
| **Through-Hole to SMT Spacing** | Min 1.50–2.00 mm | **0.330 mm** (`PI1` pad 2 to `Type_C1` S1) | **Violation** | THT wave/selective solder wash hazard |

### Solder Bridging Risk Analysis
1. **Camera Connector J1 (30-pin, 0.40 mm Pitch):** Pad size is 0.22 mm x 0.70 mm. Copper gap between pads is $0.40 - 0.22 = 0.18$ mm. With standard 0.05 mm mask expansion per side, the remaining solder mask web is only $0.18 - 0.10 = 0.08$ mm. If JLCPCB cannot maintain an 0.08 mm dam, pins will be ganged under one mask aperture, resulting in solder bridging across CSI differential pairs during reflow.
2. **USB Multiplexer U6 (UQFN-10, 0.40 mm Pitch):** Pad width is 0.20 mm. Gap is 0.20 mm. Solder mask dam is 0.10 mm. This meets the minimum threshold, but paste stencil aperture reduction of 15–20% is essential to avoid bridging.
3. **Mezzanine Connector Module1 (2x 100-pin, 0.40 mm Pitch):** 200 pads of 0.20 mm width on 0.40 mm pitch. Solder mask dam is 0.10 mm.

---

## 4. Courtyard Analysis

| Item / RefDes | Layer | Status | Measured Value | Consequence / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **HDMI1 (`Molex_47151-0001`)** | `F.Cu` | **Missing Courtyard** | 0 courtyard primitives | Footprint lacks `F.CrtYd` layer; KiCad cannot check collisions |
| **DSI1 <-> HDMI1** | `F.Cu` | **Overlapping Bounding Box** | 5.630 mm (Y) x 0.10 mm (X) | Connectors touch along top edge; pad-to-pad is 0.65 mm |
| **PI1 <-> Type_C1** | `F.Cu` | **Courtyard Proximity** | 0.195 mm courtyard clearance | Pad-to-pad is only 0.33 mm between 5V pin and GND shield |
| **R36 <-> R35** | `F.Cu` | Tight Courtyard | 0.060 mm clearance | 0402 grid pitch (1.00 mm); acceptable physical body clearance |
| **R8 <-> R11** | `B.Cu` | Tight Courtyard | 0.060 mm clearance | 0402 grid pitch (1.12 mm); acceptable physical body clearance |
| **C24 <-> R20** | `F.Cu` | Tight Courtyard | 0.070 mm clearance | 0402 grid pitch (1.00 mm); acceptable physical body clearance |
| **R16 <-> C21** | `F.Cu` | Tight Courtyard | 0.070 mm clearance | 0402 grid pitch (1.00 mm); acceptable physical body clearance |
| **C6 <-> C16 <-> C8** | `F.Cu` | Tight Courtyard | 0.080 mm clearance | 0402 grid pitch (1.00 mm); acceptable physical body clearance |
| **C19 <-> C27** | `F.Cu` | Tight Courtyard | 0.080 mm clearance | 0402 grid pitch (1.00 mm); acceptable physical body clearance |
| **R22 <-> R24 <-> R28 <-> R33** | `B.Cu` | Tight Courtyard | 0.140 mm clearance | 0402 bank; acceptable |
| **U2 <-> Q1** | `B.Cu` | Tight Courtyard | 0.150 mm clearance | SOT-23-5 to SOT-523; pad clearance is 0.70 mm |

---

## 5. Mechanical Keepout & Interface Evaluation

### 5.1 4x M2.5 Mounting Holes Evaluation
Raspberry Pi Compute Module 4 and 5 mechanical standards mandate four M2.5 mounting holes arranged symmetrically around the mezzanine connectors on a **48.0 mm (horizontal) x 33.0 mm (vertical)** pattern:
* **Nominal Locations:** (24.80, 28.42), (72.80, 28.42), (24.80, 61.42), and (72.80, 61.42).
* **Required Hole Spec:** 2.7 mm NPTH drill with a concentric **5.0 mm diameter keepout zone** (2.5 mm radius) on both sides for standoff bodies, screw heads, or threaded spacers.

#### Keepout Violations at Standard Mounting Locations:
1. **Bottom-Right Corner (72.80, 61.42): CRITICAL CONFLICT**
   * **Capacitor C4 (10 µF, 0805 on `B.Cu`):** Placed at (71.00, 61.00), only **1.85 mm** from the hole center. An 0805 body extends $\pm 1.0$ mm, placing it directly under a 5.0 mm standoff or screw head. Installing hardware will physically crush `C4`.
   * **Power Via `/CM5_5V`:** Placed at (71.94, 62.28), only **1.22 mm** from hole center. Standoff pressure will short 5V power to the mounting screw/ground.
   * **Ground Via `GND`:** Placed at (72.46, 64.17), 2.77 mm from center.
2. **Top-Left Corner (24.80, 28.42): HIGH CONFLICT**
   * **Signal Via `/HDMI0_HOTPLUG`:** Placed at (24.31, 29.36), only **1.06 mm** from hole center. Direct mechanical screw head short/crush risk.
   * **Power Via `/HDMI_5V`:** Placed at (25.50, 31.16), 2.83 mm from hole center.
   * **I2C Via `/HDMI0_SDA`:** Placed at (26.50, 30.84), 2.96 mm from hole center.
   * **Ground Via `GND`:** Placed at (23.40, 26.20), 2.62 mm from hole center.
3. **Top-Right Corner (72.80, 28.42):**
   * Power Via `/CM5_5V` at (74.00, 25.80), 2.88 mm from center.
4. **Bottom-Left Corner (24.80, 61.42):**
   * Ground Via `GND` at (23.40, 63.80), 2.76 mm from center.
5. **Physical Hole Status:** **0 mounting holes exist on this board.** The carrier board cannot be mechanically fastened to the CM5 module or enclosure.

---

### 5.2 Connector Overhangs & Board Edge Alignment
Board outline is [21.50, 76.50] mm in X (55.0 mm wide) and [25.00, 65.00] mm in Y (40.0 mm high) with 3.0 mm corner radii.

| Connector | Placement (X, Y, Rot) | Layer | Orientation / Mouth Direction | Extent Relative to Edge | DFM / Usability Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Type_C1** (USB Type-C) | (31.00, 62.50, 0°) | `F.Cu` | Mouth faces Bottom (+Y, 65.0 mm) | **+1.18 mm Overhang** past 65.0 mm edge | **Correct**: Protrudes past board edge for enclosure panel mating |
| **TF1** (Micro-SD Card) | (29.00, 43.50, -90°) | `F.Cu` | Slot faces Left (-X, 21.5 mm) | **0.48 mm Inside** left board edge | **Correct**: Inserted Micro-SD card will overhang 1.5–2.0 mm for push-push ejection |
| **HDMI1** (Mini-HDMI Type-C) | (29.50, 30.52, 180°) | `F.Cu` | Mouth faces Top (-Y, 25.0 mm) | **1.02 mm Inside** top board edge (pads sit 2.0 mm inside) | **Acceptable / Flush**: Shell mouth sits flush/slightly recessed with top edge |
| **J2** (USB-A Single Port) | (65.00, 31.50, 0°) | `F.Cu` | **Vertical** (mouth points UP normal to board) | Sits 1.45 mm inside right edge, 1.60 mm inside top edge | **Check Enclosure Height**: Vertical USB-A is ~15 mm tall; no horizontal overhang |
| **DSI1** (15-pin DSI FPC) | (48.50, 29.39, 180°) | `F.Cu` | Actuator faces Top (-Y, 25.0 mm) | Connector body sits 0.20 mm inside top edge; **Silkscreen clipped by 0.03 mm** | **Warning**: DRC reports silk edge clearance violation (0.03 mm actual vs 0.15 mm rule) |
| **PI1** (40-Pin GPIO Header) | (25.00, 55.77, 90°) | `F.Cu` | Pin 1 at (25.0, 55.8), Pin 40 at (73.3, 53.2) | Header body spans X = [23.6, 74.6] mm (2.1 mm inside left, 1.9 mm inside right) | **Fits Within Board**: 51 mm long dual-row header runs horizontally across lower section |

---

### 5.3 Compute Module 5 (Module1) Mezzanine Clearance
* **Mating Topology:** The CM5 module mates onto `B.Cu` via two DF40 100-pin connectors.
* **Component Population on Mating Face:** 54 components sit on `B.Cu` directly in the footprint envelope of the CM5 module.
* **Height Stackup Crisis:**
  * Hirose DF40C standard receptacle stack height: **1.5 mm**.
  * SOT-23-5 IC height (`U1`, `U2`, `U3`, `U4`, `U7`, `U8`): **1.45 mm maximum**.
  * Remaining clearance under CM5 module: $1.50 - 1.45 = \mathbf{0.05\ \text{mm}}$ (50 µm).
  * Any PCB warpage, solder fillet thickness, or component on the underside of the CM5 module will cause direct physical interference.
* **Through-Hole Component Lead Collision:**
  * `H3` (`CM5:PinHeader_1x03_P2.54mm_Vertical`) is placed directly on `B.Cu` at (67.00, 49.54). **This header must be removed or moved to `F.Cu`.**
  * THT pin leads from `PI1` (40 pins), `H4` (3 pins), `H5` (3 pins), and `J2` (7 pins) penetrate to `B.Cu`. Their solder tails protrude 1.5–2.5 mm and will short against the CM5 module underside unless clipped completely flush and masked, or unless a 3.0 mm stack-height connector (`DF40HC(3.0)-100DS-0.4V`) is used.

---

## 6. Prioritized Remediation Action Plan

### Priority 1: Critical Mechanical Fixes (Fab & Assembly Blockers)
1. **Add 4x M2.5 Mounting Holes:**
   * Place `Mounting_Hole_M2.5` footprints (2.7 mm drill NPTH, 5.0 mm keepout) at the 4 standard CM4/CM5 coordinates: (24.80, 28.42), (72.80, 28.42), (24.80, 61.42), and (72.80, 61.42).
   * **Relocate C4:** Move `C4` (0805 on `B.Cu`) away from (71.00, 61.00) to clear the 5.0 mm keepout circle around (72.80, 61.42).
   * **Reroute Vias in Standoff Keepouts:** Relocate `/CM5_5V` via at (71.94, 62.28) and `/HDMI0_HOTPLUG` via at (24.31, 29.36) to maintain $\ge 3.0$ mm clearance from hole centers.
2. **Remove or Flip H3 to Top Side:**
   * Move `H3` from `B.Cu` to `F.Cu`, or replace it with a right-angle/SMD connector outside the CM5 envelope.
3. **Mandate Tall Mezzanine Stack Height:**
   * Change the BOM and assembly MPN from `DF40C-100DS-0.4V` (1.5 mm) to `DF40HC(3.0)-100DS-0.4V` (3.0 mm) to provide 1.55 mm of headroom over SOT-23-5 packages and THT lead tails.

### Priority 2: SMT Assembly & Solder Bridge Mitigations
1. **Add Courtyard to HDMI1:**
   * Update footprint `CM5:HDMI_Mini-C_Molex_47151-0001` to define `F.CrtYd` with 0.25 mm boundary extension.
2. **Increase PI1 to Type_C1 Clearance:**
   * Shift `Type_C1` slightly right (+X by 0.5–1.0 mm) or adjust `PI1` to increase pad clearance from 0.33 mm to $\ge 1.0$ mm.
3. **Enforce Stencil Aperture Reductions on Fine-Pitch Parts:**
   * For `J1` (0.4 mm pitch camera connector) and `U6` (0.4 mm pitch UQFN), specify 15–20% paste reduction in the assembly notes to prevent solder bridges.
4. **Fix Silkscreen Edge Clipping on DSI1:**
   * Retract `DSI1` silkscreen boundary by 0.15 mm to satisfy board edge clearance.
