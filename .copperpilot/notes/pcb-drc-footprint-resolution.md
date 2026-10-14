# PCB Layout, Footprint Integrity, and DRC Resolution Strategy

**Document Path:** `./.copperpilot/notes/pcb-drc-footprint-resolution.md`  
**Date:** 2026-10-14  
**Project:** Raspberry Pi Compute Module 5 AI Camera Carrier Board (`CM5-AI-Cam-CopperPilot`)  
**Target Fabricator:** JLCPCB 6-Layer Standard Process with Double-Sided SMT Assembly  

---

## 1. Executive Summary

An in-depth structural and geometrical audit of `CM5-AI-Cam-CopperPilot.kicad_pcb` was performed using `kicad-cli 10.0.3` and automated S-expression extraction. The board currently exhibits **1,601 DRC violations**, **10 unconnected net segments**, and a critical **footprint assignment anomaly** where only 45 components are placed (out of 103 defined in the schematic), with footprints severely scrambled (e.g., capacitors placed on SOT-23-5 land patterns, Mini-HDMI mapped to an inductor, and 0402 resistors mapped to whole SD card sockets).

This document establishes the exact root causes for every DRC violation category and outlines an end-to-end resolution roadmap to bring the board into full compliance with JLCPCB 6-layer manufacturing and double-sided PCBA standards.

---

## 2. Root Cause Analysis of 1,601 DRC Violations

The current board setup in `CM5-AI-Cam-CopperPilot.kicad_pro` enforces conservative default constraints (designed for coarse 2-layer boards) that conflict directly with the high-density interconnect (HDI) geometry actually used to route the CM5 carrier:

| DRC Violation Type | Count | Current Constraint Setting | Actual Board Geometry | JLCPCB 6-Layer Capability | Root Cause & Resolution |
|---|---:|---|---|---|---|
| **Clearance** | 499 | `clearance = 0.20 mm` | `0.1217 mm` (approx. 4.8 mil) | Min `0.09 mm` (3.5 mil); standard `0.127 mm` (5 mil) | Board was routed at ~5 mil clearance, violating the 0.20 mm default. Update netclass clearance to `0.127 mm` / `0.15 mm`. |
| **Drill Out of Range** | 199 | `min_through_hole_diameter = 0.30 mm` | `0.20 mm` and `0.25 mm` via drills | Min `0.15 mm` (limit), `0.20 mm` (standard) | Vias use 0.20/0.25 mm drills. Update `min_through_hole_diameter` to `0.20 mm`. |
| **Track Width** | 199 | `min_track_width = 0.20 mm` | `0.15 mm` (signal), `0.125 mm` (diff pairs) | Min `0.09 mm` (limit), `0.10 mm` (high-speed) | Update `min_track_width` in `.kicad_pro` to `0.09 mm`. |
| **Via Diameter** | 199 | `min_via_diameter = 0.50 mm` | `0.35 mm` and `0.45 mm` | Min `0.25 mm` (microvia), `0.40 mm` (standard mechanical) | Vias use 0.35/0.45 mm pads. Update `min_via_diameter` to `0.40 mm` (or `0.35 mm`). |
| **Annular Width** | 198 | `min_via_annular_width = 0.10 mm` | `0.075 mm` (0.35 mm pad - 0.20 mm drill / 2) | Min `0.075 mm` (limit), `0.10 mm` (standard) | Vias with 0.35 mm pad / 0.20 mm drill have 0.075 mm annular ring. Update constraint or standardize on 0.40 mm pad / 0.20 mm drill. |
| **Hole Clearance** | 122 | `min_hole_clearance = 0.25 mm` | `0.1967 mm` (track to via drill) | Min `0.20 mm` | Track-to-via hole clearance violates 0.25 mm limit. Update `min_hole_clearance` to `0.20 mm`. |
| **Lib Footprint Issues** | 90 | Library linking | Footprint library table lookup | KiCad 10 project paths | Fix `${KIPRJMOD}` resolution in fp-lib-table so all footprints link to `CM5.pretty`. |
| **Copper Edge Clearance**| 53 | `min_copper_edge_clearance = 0.50 mm`| `0.30 mm` to `0.475 mm` | Min `0.20 mm` (CNC routed) | Vias and planes routed within 0.30 mm of board edge. Update constraint to `0.30 mm`. |
| **Silk Over Copper** | 27 | Solder mask / silk overlap | Silkscreen clipping pads | Min `0.15 mm` silk-to-pad clearance | Silkscreen text and component outlines encroaching on solder mask openings. Run automated silkscreen pushback. |
| **Starved Thermal** | 6 | Thermal spoke connectivity | Plane spoke count < 2 | Min 2 spokes | Ground plane necked down around dense via clusters. Add copper pour keepouts or widen relief spokes. |
| **Silk Edge Clearance** | 5 | Silk to Edge.Cuts | `< 0.20 mm` | Min `0.20 mm` | Silkscreen labels crossing the board outline. Shift labels inward >= 0.5 mm. |
| **Via Dangling** | 4 | Dangling stub vias | Unconnected via stubs on `/PWR_3V3` and `GND` | Zero tolerance | Delete orphaned stub vias from previous manual routing passes. |

---

## 3. The 10 Unconnected Net Items Breakdown

Inspection of the DRC report identified 10 unrouted/broken connections on critical functional nets:

1. **`/CSI_D0_N` (Camera MIPI Data 0 Negative):**
   - Disconnected between Pad 3 of common-mode choke `L1` (F.Cu) and Pad 23 of camera socket `J1` (F.Cu).
   - *Impact:* Total failure of MIPI CSI data reception from IMX219 sensor.
2. **`/1V2` (Camera Digital Core LDO Rail):**
   - Disconnected between Pad 4 of camera socket `J1` (F.Cu) and Track `/1V2` (B.Cu).
   - *Impact:* IMX219 sensor digital core remains unpowered (camera inoperative).
3. **`/SDA_1V8` (Camera I2C Data 1.8V):**
   - Disconnected between Pad 2 of pull-up resistor `R8` (B.Cu) and Track `/SDA_1V8`.
   - *Impact:* Camera I2C bus lacks required pull-up, resulting in camera probe failure.
4. **`/PWR_3V3` (System 3.3V Power Bus - 3 Breaks):**
   - Break 1: Between Track on B.Cu (`(37.36, 42.55)`) and Track on F.Cu (`(38.45, 48.49)`).
   - Break 2: Between Track on B.Cu (`(53.50, 47.98)`) and Via on F.Cu-B.Cu (`(54.64, 43.29)`).
   - Break 3: Between Track on B.Cu (`(53.50, 47.98)`) and Track on B.Cu (`(48.50, 47.98)`).
   - *Impact:* Power distribution interrupted to secondary-side regulators and sensors.
5. **`GND` (Ground Plane Continuity - 3 Breaks):**
   - Break 1: Via at `(45.53, 61.09)` to Track at `(47.69, 61.20)`.
   - Break 2: Track at `(53.10, 60.34)` to Track at `(51.50, 60.34)`.
   - Break 3: Track at `(54.30, 60.34)` to Track at `(53.10, 60.34)`.
   - *Impact:* Ground return loop split near 40-pin GPIO header.
6. **`/CM5_5V` (Main 5V Power Bus):**
   - Disconnected between Track at `(56.99, 63.48)` and Track at `(33.40, 58.82)`.
   - *Impact:* 5V supply fails to reach mezzanine power pins 81, 83, 85, 87, 89.

---

## 4. Footprint Assignment Mismatch Analysis

The current PCB file was initialized from a scrambled mockup netlist where footprint references were assigned arbitrarily:

| Component Ref | Schematic Value | Legitimate Footprint | Currently Placed Mockup Footprint | Critical Hazard |
|---|---|---|---|---|
| `C10` | 100nF Decoupling | `CM5:C_0402_1005Metric` | `CM5:SOT-23-5` | 2-terminal passive placed on 5-terminal IC land pattern |
| `C19` | 0.1uF Decoupling | `CM5:C_0402_1005Metric` | `CM5:Camera_Module_IMX219-D160` | Capacitor mapped to 34-pad camera connector |
| `C25` | 22uF Bulk | `CM5:C_0805_2012Metric` | `CM5:L_CommonModeChoke_Coilank_ACM1210` | Capacitor mapped to 4-pad choke |
| `HDMI1` | Mini-HDMI Type-C | `CM5:HDMI_Mini-C_Molex_47151-0001` | `CM5:L_Bourns_SRP5030CC` | 19-pin connector mapped to 2-pad power inductor |
| `DSI1` | 15-pin 1.0mm FPC | `CM5:Molex_200528-0150_1x15-1MP_P1.00mm_Horizontal`| `CM5:PinHeader_2x20_P2.54mm_Vertical` | 15-pin FPC mapped to 40-pin dual-row header |
| `Type_C1` | USB-C 16-pin | `CM5:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | `CM5:C_0805_2012Metric` | 16-pin USB-C receptacle mapped to 0805 capacitor |
| `U1` | RT9193-28GB LDO | `CM5:SOT-23-5` | `CM5:C_0402_1005Metric` | 5-pin active IC mapped to tiny 0402 footprint |
| `U6` | FSUSB42UMX USB Switch| `CM5:UQFN-10_1.4x1.8mm_P0.4mm` | `CM5:SOT-23-5` | 10-pin QFN mapped to 5-pin SOT package |
| `X1` | 24MHz Active OSC | `CM5:Crystal_SMD_3225-4Pin_3.2x2.5mm` | `CM5:MOLEX_USB_67298-4090` | 4-pin oscillator mapped to vertical USB-A socket |
| `R10` | 22R Damping Resistor | `CM5:R_0402_1005Metric` | `CM5:SDCARD_MOLEX_503398-1892` | 0402 resistor mapped to MicroSD card socket |
| `R34` | 10k Pull-up | `CM5:R_0402_1005Metric` | `CM5:Raspberry-Pi-5-Compute-Module` | 0402 resistor mapped to 200-pin mezzanine footprint |

**Action Required:** A complete forward synchronization from the validated schematic (`sync_schematic_to_pcb` with strict footprint matching) is mandatory. The PCB must be populated with all 103 legitimate footprints directly associated by symbol UUID.

---

## 5. JLCPCB SMT Pick-and-Place Rules & DFM Enhancements

### 5.1 Fiducial Marks
- JLCPCB SMT Pick-and-Place optical cameras require at least 3 global fiducials per side.
- **Specification:** Circular copper pad `1.0 mm` diameter, solder mask opening `2.0 mm` diameter, no drill hole. Solder mask keepout zone >= `3.0 mm` from any neighboring copper/trace.
- **Placement:** Place 3 asymmetric fiducials on Top layer (F.Cu) and 3 on Bottom layer (B.Cu) near board corners (`(3.0, 3.0)`, `(52.0, 3.0)`, `(3.0, 37.0)` mm relative to board origin).

### 5.2 Component Clearances
- Passive-to-passive spacing: >= `0.35 mm`
- IC-to-passive spacing: >= `0.50 mm`
- IC-to-IC spacing: >= `0.80 mm`
- Component body to board edge: >= `0.50 mm` (milled/routed), >= `1.0 mm` (V-cut)

### 5.3 Double-Sided Reflow Constraints
- Secondary side (B.Cu) components will be inverted during second-pass reflow.
- Components placed on B.Cu must have weight-to-pad-area ratio < `0.046 g/mm²` (< `30 g/in²`).
- The Compute Module 5 mezzanine connectors (`DF40C-100DS`), LDOs (`SOT-23-5`), and passives on B.Cu are well within surface tension limits and will remain securely soldered.

---

## 6. End-to-End PCB Resolution Roadmap

1. **Update KiCad Project Design Settings (`CM5-AI-Cam-CopperPilot.kicad_pro`):**
   - Write verified JLCPCB 6-layer rules into `board.design_settings.rules` (min track `0.09 mm`, min via `0.40/0.20 mm`, clearance `0.10 mm`, copper-to-edge `0.30 mm`).
   - Define net classes: `Default` (0.15/0.15 mm), `Power` (0.50/0.20 mm), `HighSpeed_90R` (0.125/0.127 mm), `HighSpeed_100R` (0.105/0.150 mm).
2. **Synchronize Schematic to PCB:**
   - Execute schematic-to-PCB synchronization. Purge all 45 mockup footprints and import all 103 correct footprints from `CM5.pretty`.
3. **Establish Placement and Fiducials:**
   - Place IMX219 camera socket (`J1`), DF40 connectors (`Module1`), USB-C, Mini-HDMI, vertical USB-A, MicroSD socket, and 40-pin GPIO matching exact mechanical specs.
   - Place 3x Top and 3x Bottom SMT fiducials.
4. **Controlled Impedance Differential Pair Routing:**
   - Route HDMI TMDS differential pairs (100Ω differential) and MIPI CSI-2 / DSI pairs (100Ω differential) on In4.Cu/F.Cu with solid ground plane references.
   - Route USB 2.0 differential pairs (90Ω differential) from USB-C and USB-A through FSUSB42UMX to CM5.
5. **Power Distribution & Plane Setup:**
   - Flood In1.Cu with solid `GND` return plane.
   - Split In2.Cu / In3.Cu for `PWR_3V3`, `CM5_5V`, and auxiliary camera power rails (`2V8`, `1V8`, `1V2`).
6. **Refill Zones and Verification:**
   - Refill all zones on all 6 layers using `kicad-cli pcb drc --refill-zones`.
   - Run DRC to confirm zero clearance, zero track width, and zero unconnected items.
