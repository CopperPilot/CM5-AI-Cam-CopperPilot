# CM5 AI Camera Carrier Board Project Index

## Project Overview
High-density carrier board designed for the Raspberry Pi Compute Module 5 (CM5), featuring an onboard 8MP Sony IMX219 camera module, Mini-HDMI video output, 15-pin DSI display connector, USB 2.0 dual-role multiplexer (USB-C flashing / vertical USB-A host), Micro SD card socket, and standard 40-pin Raspberry Pi GPIO header.

## Form Factor & Mechanics
- **Dimensions:** 55.0 mm x 40.0 mm (matching CM5 footprint)
- **Mounting:** 4x M2.5 mounting holes matching CM5 specifications
- **Corner radius:** 3.0 mm (CNC routed edge outline)
- **Stackup:** JLCPCB 6-Layer Standard Process (`JLC06161H-3313`, 1.6 mm finished thickness)

## Manufacturing Readiness & Sign-Off Status
- **Schematic ERC Status:** 0 Errors, 0 Symbol Mismatches
- **PCB DRC Status:** 0 Design Rule Violations, 0 Schematic Parity Issues
- **LCSC SMT BOM:** 100% verified active parts with C-numbers across all 90 components
- **Production Package:** `jlcpcb_production/`
  - Gerbers & Drills: `jlcpcb_production/gerbers/` and `jlcpcb_production/gerbers_jlcpcb.zip`
  - SMT Assembly: `jlcpcb_production/assembly/bom_jlcpcb.csv` & `cpl_jlcpcb.csv`
  - Electrical Test: `jlcpcb_production/netlist/CM5-AI-Cam-CopperPilot.d356`
  - Sign-off Reports: `jlcpcb_production/reports/erc_signoff.rpt` & `drc_signoff.rpt`

## Critical Engineering Remediation Summary
1. **Buck Regulator (U5 - MP1658GTF-Z):**
   - Corrected feedback divider resistor R20 to 61.9k 1% (setting `PWR_3V3` to safe 3.305V instead of destructive 4.84V).
   - Detached R16/C21 loading from the high-side BST floating rail and reconnected to SW as a proper SW-to-GND snubber.
2. **USB Multiplexer (U6 - FSUSB42UMX):**
   - Verified 10-pin UMLP-10 pinout matches official onsemi datasheet.
   - Connected R28 pullup to `CM5_3V3` so the vertical USB-A host port is active by default.
3. **Power Switches (U4, U7, U8):**
   - Verified pin compatibility with STMicroelectronics STMPS2171STR (SOT-23-5: 1=OUT, 2=GND, 3=FAULT, 4=EN, 5=IN).
4. **Common Mode Chokes (L1, L2, L3):**
   - Verified ACM1210 winding structure (Line 1: 1-2, Line 2: 4-3) to ensure differential signals pass straight through without shorts.
5. **Level Shifter (Q1, Q2 - DMG1012T-7):**
   - Verified SOT-523 pinout (1:Gate, 2:Source, 3:Drain) and eliminated redundant pull-up resistors on DSI1.
6. **JLCPCB 6-Layer Rules:**
   - Enforced 0.09mm min trace, 0.12mm clearance, 0.35/0.20mm vias, 0.075mm annular ring, and 90R/100R controlled impedance classes.
