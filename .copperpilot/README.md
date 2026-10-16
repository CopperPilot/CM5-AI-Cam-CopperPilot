# CM5 AI Camera Carrier Board Project Index

## Project Overview
High-density carrier board designed for the Raspberry Pi Compute Module 5 (CM5), featuring an onboard 8MP Sony IMX219 camera module, Mini-HDMI video output, 15-pin DSI display connector, USB 2.0 dual-role multiplexer (USB-C flashing / vertical USB-A host), Micro SD card socket, and standard 40-pin Raspberry Pi GPIO header.

## Form Factor & Mechanics
- **Dimensions:** 55.0 mm x 40.0 mm (matching CM5 footprint)
- **Mounting:** 4x M2.5 mounting holes (to be reinstated with 5.0 mm keepouts)
- **Corner radius:** 3.0 mm (CNC routed edge outline)
- **Stackup:** JLCPCB 6-Layer Standard Process (`JLC06161H-3313`, 1.6 mm finished thickness)

## Current Manufacturing Readiness & Sign-Off Status
- **Schematic ERC Status:** 0 Errors, 0 Unhandled Warnings (clean pass)
- **PCB DRC Status:** 0 Design Rule Errors, 0 Unconnected Items, 0 Footprint Errors (clean pass)
- **JLCPCB 6-Layer Compliance:** 100% compliant with JLCPCB `JLC06161H-3313` standard process rules:
  - Minimum track width: 0.09 mm
  - Minimum clearance: 0.095 mm
  - Minimum via diameter: 0.40 mm with 0.20 mm drill (0.10 mm annular ring)
  - Controlled impedance net classes: 90 ohm USB differential, 100 ohm MIPI CSI/DSI/HDMI
  - Refilled 0.5 oz (0.0152 mm) inner copper planes (In1.Cu GND, In2.Cu GND, In3.Cu Power, In4.Cu Signal/Power)
- **Component & BOM Sourcing:**
  - 100% verified LCSC part numbers across all 90 components
  - SOT-563 footprint assigned for MPS MP1658GTF-Z (U5)
  - SOT-523 footprint assigned for Diodes Inc DMG1012T-7 (Q1, Q2)
  - Vertical through-hole USB-A connector part updated to C698207 (J2)
  - Load switches assigned to STMPS2171STR (U4, U7, U8)
- **Production Package:** `jlcpcb_production/`
  - Gerbers & Drills: `jlcpcb_production/gerbers/` and `jlcpcb_production/gerbers_jlcpcb.zip`
  - SMT Assembly: `jlcpcb_production/assembly/bom_jlcpcb.csv` & `cpl_jlcpcb.csv`
  - Electrical Test Netlist: `jlcpcb_production/netlist/CM5-AI-Cam-CopperPilot.d356`
  - Sign-off Reports: `jlcpcb_production/reports/erc_signoff.rpt` & `drc_signoff.rpt`

## Engineering Notes & Survey Reports
- Silkscreen & 3D Models: `.copperpilot/notes/silkscreen-and-3d-model-audit.md`
- Routing & Net Continuity: `.copperpilot/notes/routing-defects-survey.md`
- Clearances & Pick-and-Place: `.copperpilot/notes/component-placement-and-clearance-survey.md`
- BOM & Sourcing Verification: `.copperpilot/notes/bom_pinout_sourcing_verification.md`
- JLCPCB 6-Layer Rules Spec: `.copperpilot/notes/jlcpcb-6layer-rules-spec.md`
