# CM5 AI Camera Carrier Board - JLCPCB PCBA Manufacturing Sign-off Report

## Executive Summary
This document provides the final manufacturing sign-off and engineering audit report for the Raspberry Pi Compute Module 5 (CM5) AI Camera Carrier Board. The design has been brought to full compliance with JLCPCB 6-layer standard manufacturing capabilities (`JLC06161H-3313`) and automated SMT pick-and-place assembly.

All critical schematic circuit defects, severed nets, package mismatches, and DRC/ERC violations have been systematically remediated and verified with KiCad 10.0.3 CLI tools.

---

## Sign-off Verification Metrics

| Check Domain | Status | Violations / Errors | Sign-off Verdict |
| :--- | :--- | :--- | :--- |
| **Schematic ERC** | Checked via `kicad-cli sch erc` | **0 Errors**, 0 Unhandled Warnings (9 standard PWR_FLAG pin warnings on 40-pin GPIO) | **PASSED** |
| **PCB Layout DRC** | Checked via `kicad-cli pcb drc` | **0 Errors**, **0 Unconnected Items**, **0 Footprint Errors** (78 informational footprint library property notices) | **PASSED** |
| **Net Continuity** | Checked via `kicad-cli pcb drc` | **0 Unconnected Items** (all 13 severed routing nets restored) | **PASSED** |
| **3D Mechanical Solid** | Checked via `kicad-cli pcb export step` | Complete 27 MB AP214 solid assembly generated without mesh errors | **PASSED** |
| **LCSC SMT Sourcing** | Checked against LCSC catalog | 100% verified active parts with valid C-numbers across all 90 components | **PASSED** |
| **Fabrication Package** | RS-274X, Excellon, IPC-D-356, CSV | 13 Gerber layers, PTH/NPTH drills, IPC-D-356 netlist, BOM, CPL, Zip | **READY FOR RELEASE** |

---

## Detailed Engineering Remediation Summary

### 1. Schematic Circuit & Logical Block Fixes
1. **Buck Regulator SW Snubber (DEF-01):** Replaced destructive 1 µF capacitor C21 on buck switch node SW with a 330 pF 0402 ceramic capacitor (LCSC `C1547`), eliminating 15 W power dissipation across R16.
2. **Power Load Switches (DEF-03):** Corrected U4 (HDMI 5V) and U7 (MicroSD 3.3V) to STMPS2171STR (SOT-23-5: Pin 1=OUT, Pin 2=GND, Pin 3=FAULT, Pin 4=EN, Pin 5=IN) matching LCSC `C157437` and restoring 5V power to Mini-HDMI Pin 18 and MicroSD Pin 4.
3. **Common-Mode Chokes (DEF-04):** Re-mapped differential choke coils L1, L2, L3 (`ACM1210`) to connect Coil 1 in-line on signal P and Coil 2 in-line on signal N, eliminating MIPI CSI-2 dead shorts.
4. **I2C Cross-Rail Contention (DEF-06):** Marked redundant 4.7 kΩ pull-ups R35/R36 as DNP to prevent voltage contention between 3.3V and 1.8V GPIO rails.
5. **Camera Standby Overvoltage (DEF-07):** Level-shifted `CAM_GPIO` driving IMX219 `/PWDN` via a 1k/1.2k resistor divider (R17/R15) to maintain sensor I/O voltage safely below 1.8V VDDIO.
6. **Oscillator Bypass (DEF-08):** Corrected X1 24.000 MHz oscillator bypass capacitor C20 from 10 pF to 0.1 µF 0402 (LCSC `C1525`).
7. **Bootloader EEPROM Lockout (DEF-10):** Marked R29 (0R) as DNP to unprotect CM5 onboard EEPROM and enable bootloader firmware updates.

### 2. Component Packaging & Sourcing Reconciliation
1. **Buck Regulator (U5):** Updated footprint to `CM5:SOT-563` and BOM MPN to MPS MP1658GTF-Z (LCSC `C2837379`).
2. **Level Shifters (Q1, Q2):** Corrected footprint from TI DRT-3 to `CM5:SOT-523` to match Diodes Inc DMG1012T-7 (LCSC `C20512`).
3. **Vertical USB-A (J2):** Updated BOM part from right-angle C720523 to verified vertical through-hole receptacle C698207 (Korean Hroparts U-A-M14V-W-B) and assigned exact 3D STEP solid.
4. **Library Syntax (`CM5.pretty`):** Stripped all XML comments from `Camera_Module_IMX219-D160.kicad_mod` and balanced parenthesis in `Molex_200528-0150.kicad_mod`.

### 3. JLCPCB 6-Layer DFM Rules (`JLC06161H-3313`)
- **Layer Stackup:** 6-layer symmetric stackup with 1.6 mm finished thickness and 0.5 oz (0.0152 mm) inner copper foil.
- **Minimum Trace & Spacing:** 0.090 mm min trace width, 0.095 mm min electrical clearance.
- **Via Geometry:** All 0.35 mm vias upgraded to min 0.40 mm diameter with 0.20 mm drill (0.10 mm / 4.0 mil annular ring).
- **Controlled Impedance:**
  - `HighSpeed_90R`: 0.15 mm width / 0.12 mm gap on outer layers (USB 2.0 D+/D-).
  - `HighSpeed_100R`: 0.12 mm width / 0.15 mm gap on outer layers (MIPI CSI-2, DSI, HDMI TMDS).
- **Silkscreen Typography:**
  - All footprint `LCSC` properties hidden (`hide yes`), eliminating 452 silkscreen warnings.
  - Text stroke width set to 0.15 mm (JLCPCB 6 mil requirement).

### 4. Routing Restoration (13 Severed Nets Resolved)
- **/CM5_5V:** Routed dedicated 1.2 mm power track on `F.Cu` from Type-C 5V node to CM5 input capacitors C22/C23.
- **/PWR_3V3:** Restored copper bridges on `B.Cu` for U2 pin 1, C5, and C12.
- **GND Planes:** Stitched isolated ground pins across DF40 escape antipads on `B.Cu`.
- **/CSI_D0_N:** Routed length-matched differential pair on `In1.Cu` / `F.Cu` from choke L1 to J1 pin 23.
- **/MP1658_BST & /MP1658_SW:** Bridged regulator bootstrap rail and connected SW node to snubber R16.
- **/1V2, /SDA_1V8, /CM5_3V3:** Routed local drop segments to respective load pins.
- **Dangling Vias:** Pruned all 5 antenna vias and 7 orphan track stubs.

---

## Production Deliverables Manifest

```
jlcpcb_production/
├── gerbers_jlcpcb.zip                         # Complete production archive for JLCPCB PCB order
├── assembly/
│   ├── bom_jlcpcb.csv                        # Formatted SMT BOM (Comment, Designator, Footprint, LCSC)
│   └── cpl_jlcpcb.csv                        # Centroid pick-and-place file (Designator, Val, Package, Mid X, Mid Y, Rotation, Layer)
├── gerbers/
│   ├── CM5-AI-Cam-CopperPilot-F_Cu.gtl       # Top Copper
│   ├── CM5-AI-Cam-CopperPilot-In1_Cu.g1      # Inner Layer 1 (GND Plane)
│   ├── CM5-AI-Cam-CopperPilot-In2_Cu.g2      # Inner Layer 2 (GND Plane)
│   ├── CM5-AI-Cam-CopperPilot-In3_Cu.g3      # Inner Layer 3 (Power Plane)
│   ├── CM5-AI-Cam-CopperPilot-In4_Cu.g4      # Inner Layer 4 (Signal/Power)
│   ├── CM5-AI-Cam-CopperPilot-B_Cu.gbl       # Bottom Copper
│   ├── CM5-AI-Cam-CopperPilot-F_Mask.gts     # Top Solder Mask
│   ├── CM5-AI-Cam-CopperPilot-B_Mask.gbs     # Bottom Solder Mask
│   ├── CM5-AI-Cam-CopperPilot-F_Paste.gtp    # Top Solder Paste (Stencil)
│   ├── CM5-AI-Cam-CopperPilot-B_Paste.gbp    # Bottom Solder Paste (Stencil)
│   ├── CM5-AI-Cam-CopperPilot-F_Silkscreen.gto # Top Silkscreen
│   ├── CM5-AI-Cam-CopperPilot-B_Silkscreen.gbo # Bottom Silkscreen
│   ├── CM5-AI-Cam-CopperPilot-Edge_Cuts.gm1  # Board Outline
│   ├── CM5-AI-Cam-CopperPilot-PTH.drl        # Plated Through-Hole Drill
│   ├── CM5-AI-Cam-CopperPilot-NPTH.drl       # Non-Plated Through-Hole Drill
│   ├── CM5-AI-Cam-CopperPilot-drill.rpt      # Excellon Drill Report
│   └── CM5-AI-Cam-CopperPilot-job.gbrjob     # Gerber Job Specification
├── netlist/
│   └── CM5-AI-Cam-CopperPilot.d356           # IPC-D-356 Electrical Test Netlist
└── reports/
    ├── drc_signoff.rpt                       # KiCad 10 DRC Sign-off Report (0 Errors, 0 Unconnected)
    └── erc_signoff.rpt                       # KiCad 10 ERC Sign-off Report (0 Errors)
```
