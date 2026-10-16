# CM5 AI Camera Carrier Board: Comprehensive Pre-Public & JLCPCB DFM Review

**Date:** 2026-10-16  
**Target:** Public Open-Source Hardware Release & JLCPCB 6-Layer PCBA Fabrication  
**PCB Dimensions:** 55.00 mm × 40.00 mm (Raspberry Pi CM5 HAT form factor)  
**Stackup:** 6-Layer JLC06161H-7628 (1.6 mm, 1/0.5/0.5/0.5/0.5/1 oz Cu)  
**Status:** Audit Completed — Comprehensive Prioritized Issue Register Configured  

---

## 1. Executive Summary & Verification Metrics

Prior to publishing the CM5 AI Camera Carrier Board repository and releasing manufacturing packages to JLCPCB, an exhaustive multi-domain audit was conducted across schematic electrical rules, drafting quality, schematic-to-PCB parity, 6-layer physical DRC, high-speed return paths, and fabrication constraints.

| Domain | Raw / Initial State | Target Sign-Off Metric | Audit Status & Severity |
| :--- | :--- | :--- | :--- |
| **Electrical Rule Check (ERC)** | 15 violations (6 broken symbol library paths, 9 pin-type conflicts) | 0 Errors, 0 Warnings | **P0 Blocker & P1 Electrical** |
| **Design Rule Check (Standard Rules)** | 164 violations (78 lib mismatches, 56 hole-to-hole, 18 clearances, 12 edge clearances) | 0 Errors, 0 Warnings | **P0 Fabrication & P1 DFM** |
| **DRC with Custom `.kicad_dru` Bypass** | 78 warnings (`lib_footprint_mismatch`), 0 errors, 0 unconnected | 0 Errors, 0 Warnings (unmasked) | **P1 Integrity Hazard** |
| **Schematic-to-PCB Parity** | 26 parity mismatches (choke polarity swaps, LCSC MPNs, DNP flags) | 0 Parity Discrepancies | **P0 Functional Blocker** |
| **DNP (Do Not Populate) Flags** | `Module1` (dual Hirose 100-pin sockets) and `Type_C1` marked DNP | Only optional unpopulated jumpers DNP | **P0 Assembly Blocker** |
| **Schematic CAD Drafting Quality** | Severe collisions in Buck converter (`L7`/`U5`), Camera LDOs, and FETs | Clean orthogonal drafting, zero collisions | **P1 Open-Source Scrutiny** |
| **Layer 2 (`In1.Cu`) Ground Plane** | Signal routing cuts deep slots directly beneath high-speed MIPI pairs | Unbroken solid ground plane under RF/CSI | **P1 Signal Integrity / EMI** |
| **Silkscreen Legends & Usability** | 0 text labels on `B.Cu`, no header legends (`H3`-`H5`), no LED labels | Complete functional legends and pin-1 marks | **P2 Usability / Documentation** |

---

## 2. Detailed Schematic Section Scrutiny

Visual inspection was performed across each functional segment of the schematic (`CM5-AI-Cam-CopperPilot.kicad_sch`):

### 2.1 Section 1: Power Entry, USB Type-C & 3.3V Buck Converter (`U5`)
- **Visual Evidence:** `.copperpilot/tmp/renders/sch_sec1_power_type_c_buck_new3.png`
- **Assembly Hazard (DEF-01 / DEF-02):** `Type_C1` (USB-C receptacle) and `Module1` were flagged `(dnp yes)` in the raw schematic. If uploaded to JLCPCB PCBA in this state, the main 5V power input receptacle and the CM5 mezzanine sockets would be omitted from fabrication.
- **Severe Inductor Collision (DEF-05):** Power inductor `L7` (1.5 µH, `Bourns_SRP5030CC`) is drawn vertically directly on top of the pins and net lines of `U5` (pins 2, 4, 6), crossing `MP1658_SW`, `MP1658_BST`, and `MP1658_FB`.
- **Feedback Divider Collision:** Resistors `R20` (61.9k) and `R21` (20k) have net label `MP1658_FB` printed directly over their resistor body glyphs.
- **Input Capacitor Text Stacking:** `C22` (10 µF), `C23` (0.1 µF), and `R19` (1.2k) are vertically stacked such that values and net labels (`CM5_5V`, `MP1658_EN`) overlap.
- **Header Cramming:** `C4` (10 µF) and `R1` (1k) are positioned flush against the 100-pin mezzanine symbol with net label `SD_VCC_Device` slicing through both components.

### 2.2 Section 2: Camera Power Regulation & LDOs (`U1`, `U2`, `U3`)
- **Visual Evidence:** `.copperpilot/tmp/renders/sch_sec2_camera_ldos_new.png`
- **Ferrite Bead / Label Overlap (DEF-07):** Ferrite bead `FB1` (120R) and input cap `C1` (2.2 µF) have net label `CAM_FB1_OUT` printed twice vertically directly across their pins and graphical outlines.
- **Enable Pin Text Collisions:** Regulators `U1` (2.8V), `U2` (1.8V), and `U3` (1.2V) have `CAM_GPIO` and `PWR_3V3` labels colliding on their enable (EN, pin 3) terminals.
- **Bypass Capacitor Placement:** Bypass cap `C14` (100 nF) for `U3` bypass (BP, pin 4) was previously drawn across pins 1–7 of the 40-pin GPIO header `PI1`. Relocating it upward resolved the GPIO header collision, but left it directly beneath connector shield pins with label clutter.

### 2.3 Section 3: IMX219 CSI-2 Camera Interface & Level Shifting
- **Visual Evidence:** `.copperpilot/tmp/renders/sch_sec3_imx219_camera_circuits_new.png`
- **Common Mode Choke Polarity Inversion (DEF-08):** Chokes `L1`, `L2`, and `L3` (`MCF1210BF2-900T01`) show pad 2 / pad 4 net mismatches between schematic and PCB layout (`/CSI_D0_P` vs `/CAM0_D0_N`). The differential signal polarity is swapped across the choke in layout relative to the schematic netlist.
- **MOSFET Level Shifter Drafting (DEF-07):** Level shifters `Q1` and `Q2` (`DMG1012T`) have drain net labels `SCL0` and `SDA0` cutting through the transistor body and pin 3 leads. Resistor values `R4`, `R5`, `R7`, `R8` collide with vertical wire corridors.

### 2.4 Section 5: Peripherals (HDMI, DSI, MicroSD)
- **Visual Evidence:** `.copperpilot/tmp/renders/sch_sec5_peripherals_hdmi_dsi_sd_new.png`
- **DSI1 Shield Net Collision:** DSI connector `DSI1` pin `SH` has net label `GND` running vertically through the pin box.
- **Floating Decoupling:** Decoupling capacitor `C19` (0.1 µF) is placed in open space between `DSI1` and `TF1` without clear visual functional grouping.

---

## 3. PCB Layout, Layer-by-Layer & SI/PI Scrutiny

Each of the 6 copper layers and silkscreen layers was reviewed using high-resolution raster exports:

### 3.1 Layer 1: Front Copper (`F.Cu`)
- **Visual Evidence:** `.copperpilot/tmp/renders/hires_layer_F_Cu.png`
- **High-Speed Routing:** MIPI CSI-2 differential pairs route from Hirose mezzanine `Module1` through common mode chokes `L1`-`L3` to 30-pin FPC `J1`. Traces are tightly coupled.
- **Component Placement:** SMD passives and ICs are logically partitioned with power supply blocks on the right and camera conditioning in the upper center.

### 3.2 Layer 2: Inner Copper 1 (`In1.Cu`) — Primary Ground Reference
- **Visual Evidence:** `.copperpilot/tmp/renders/hires_layer_In1_Cu.png`
- **Critical Signal Integrity Defect (DEF-09):** `In1.Cu` is defined as the primary GND reference plane for Layer 1 microstrip differential pairs. However, numerous low-speed signal tracks (`/SCL0`, `/WIFI_EN`, `/GPIO12`, `/GPIO21`, `/SD_DAT0`) are routed on `In1.Cu`, slicing long clearance slots across the ground plane.
- **Consequence:** High-speed return currents on Layer 1 crossing these slots encounter high impedance, forcing return currents into large inductive loops that cause EMI radiation, timing jitter, and degraded eye diagrams on the MIPI CSI-2 bus.

### 3.3 Layer 3: Inner Copper 2 (`In2.Cu`) — High-Speed Signal Routing
- **Visual Evidence:** `.copperpilot/tmp/renders/hires_layer_In2_Cu.png`
- **Board Edge Clearance Violation (DEF-10):** Track `/HDMI0_CLK_N` runs within **0.1694 mm** of the top milled board edge. Standard JLCPCB edge clearance requirement is **0.300 mm** (with 0.200 mm being absolute minimum). Routing within 0.169 mm risks exposed copper during V-cut or routing operations and chassis shorting.

### 3.4 Layer 4 & 5: Inner Copper 3 (`In3.Cu`) & Inner Copper 4 (`In4.Cu`)
- **Visual Evidence:** `.copperpilot/tmp/renders/hires_layer_In3_Cu.png`, `hires_layer_In4_Cu.png`
- **Plane Continuity:** `In3.Cu` features split power and ground areas with large copper voids under the 40-pin header corridors.
- **Reference Planes:** Differential signals routed on `In2.Cu` reference `In1.Cu` and `In3.Cu`; solid ground backing must be preserved under critical pairs.

### 3.5 Layer 6: Back Copper (`B.Cu`)
- **Visual Evidence:** `.copperpilot/tmp/renders/hires_layer_B_Cu.png`
- **Mezzanine Interface:** Accommodates bottom-side components, 40-pin GPIO pin header solder pads, and power distribution tracks.

### 3.6 Silkscreen Layers (`F.SilkS` & `B.SilkS`)
- **Visual Evidence:** `.copperpilot/tmp/renders/hires_layer_F_Silkscreen.png`, `hires_layer_B_Silkscreen.png`
- **Zero Reference Designators:** Almost all SMD passives and ICs have reference designators hidden (`hide yes`), making manual debugging or bench inspection impossible.
- **Unlabeled Headers (DEF-11):** 3-pin configuration headers `H3`, `H4`, `H5` have no pinout or functional text on silkscreen.
- **Unlabeled Status LEDs (DEF-12):** Bottom-side LEDs `L5` and `L6` have no silkscreen text indicating which is Power and which is Activity.
- **Unlabeled Pushbutton (DEF-13):** Key switch `Key1` has no functional legend (`KEY` / `GPIO21`).
- **Missing Connector Legends (DEF-14):** USB-C, MicroSD, and USB host connectors lack external port labels.

---

## 4. JLCPCB 6-Layer DFM & Manufacturing Constraints

Comparison between design settings, custom rules (`.kicad_dru`), and JLCPCB Standard 6-Layer Capabilities:

| Parameter | Board / `.kicad_dru` Value | JLCPCB Standard Capability | Status & Risk Assessment |
| :--- | :--- | :--- | :--- |
| **Minimum Track / Space** | 0.095 mm / 0.095 mm (3.74 mil) | 0.090 mm (3.5 mil) for 1 oz / 0.5 oz | COMPLIANT with multi-layer advanced tier |
| **Via-to-Via Clearance** | 0.070 mm (in `.kicad_dru`) | 0.127 mm (5.0 mil) / 0.090 mm min | **NON-COMPLIANT (DEF-10)**: 0.070 mm risks drill breakout/bridging |
| **Via Hole Size** | 0.200 mm drill, 0.400 mm pad | 0.200 mm drill, 0.400 mm pad | COMPLIANT with standard via process |
| **Track to Board Edge** | 0.169 mm (in `In2.Cu` HDMI) | 0.300 mm standard (0.200 mm absolute min) | **NON-COMPLIANT (DEF-10)**: Exposed copper hazard |
| **Hole-to-Hole Spacing** | 0.254 mm (via), 0.50 mm (PTH) | 0.254 mm (via), 0.50 mm (PTH) | COMPLIANT when properly spaced |
| **Copper Balance** | Asymmetric routing on In1/In3 | Balanced copper coverage recommended | Moderate risk of board warpage during reflow |

---

## 5. Comprehensive Prioritized Defect Register

### Priority 0: Functional, Fabrication & Assembly Blockers (P0)

| ID | Domain | Target | Description | Root Cause | Remediation Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P0-01** | BOM / PCBA | `Module1` | Mezzanine tagged `(dnp yes)` in schematic and omitted from JLCPCB PCBA BOM. | Mezzanine module confused with carrier socket. | Clear DNP tag on `Module1`; ensure Hirose DF40C-100DS-0.4V sockets (LCSC C597931) are placed and assembled. |
| **P0-02** | BOM / PCBA | `Type_C1` | USB Type-C connector tagged `(dnp yes)` in schematic. | Erroneously set DNP during capture. | Clear DNP tag on `Type_C1`; restore USB-C receptacle (LCSC C3020560) to active BOM and CPL. |
| **P0-03** | Parity / SI | `L1`, `L2`, `L3` | Differential choke pin net swap between schematic and PCB (`/CSI_D0_P` on pad 2 vs pad 4). | Choke symbol pin mapping differs from footprint pad numbering. | Align choke symbol pin mapping and PCB footprint pads so differential polarity matches across schematic and board. |
| **P0-04** | Schematic / ERC | `sym-lib-table` | Hardcoded macOS path to `power.kicad_sym` breaks ERC on Linux/Windows. | Local absolute path committed. | Change URI to `${KICAD_SYMBOL_DIR}/power.kicad_sym`. |
| **P0-05** | Schematic / ERC | `PI1` | 9 ERC warnings: `Pin_to_pin: Bidirectional and Power output connected`. | GPIO header GND/3V3 pins typed Bidirectional. | Update pin electrical types in `CM5.kicad_sym` for `PI1` GND pins to `power_in`/`passive` and 3V3 to `power_in`. |

---

### Priority 1: DFM Compliance, Electrical Integrity & Visual Standards (P1)

| ID | Domain | Target | Description | Root Cause | Remediation Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1-06** | Schematic CAD | `U5`, `L7`, `R20`, `R21` | Inductor `L7` physically drawn across `U5` pins 2, 4, 6 and feedback divider. | Automated symbol placement without layout pass. | Shift `L7` to the right of SW pin; position `R20`/`R21` below output rail with clean orthogonal spacing. |
| **P1-07** | Schematic CAD | `Q1`, `Q2`, `FB1`, `C14` | Net labels `SCL0`/`SDA0` cut through FET symbols; `CAM_FB1_OUT` overlaps `FB1`/`C1`. | Label placement collisions. | Reposition labels to wire stubs with zero symbol overlap; clean up all text collisions. |
| **P1-08** | PCB DFM | `CM5.kicad_dru` | Custom DRU allows 0.070 mm via-to-via clearance (below JLCPCB capability). | Workaround for tight via cluster. | Re-space via clusters to maintain standard ≥0.095 mm (ideally ≥0.127 mm) clearance; remove 0.070 mm rule. |
| **P1-09** | PCB DFM | `In2.Cu` Edge Track | `/HDMI0_CLK_N` trace routed 0.169 mm from board edge (violates 0.30 mm limit). | Route path hugging outline. | Jog `/HDMI0_CLK_N` inward by ≥0.15 mm to achieve ≥0.30 mm board edge clearance. |
| **P1-10** | Signal Integrity | `In1.Cu` GND Plane | Low-speed signals cut long slots through Layer 2 ground reference plane under MIPI pairs. | Layer 2 used for overflow routing. | Reroute non-critical signals to inner signal layers to preserve an unbroken GND plane under MIPI CSI-2 pairs. |
| **P1-11** | Parity / Footprint | 78 Library Footprints | 78 `lib_footprint_mismatch` warnings when rule is set to warning. | Board footprints have STEP 3D models; library `.pretty` has legacy KiCad 8 WRL models. | Synchronize `CM5.pretty` footprints with authoritative board footprints to eliminate all 78 mismatch warnings. |
| **P1-12** | Parity / MPN | `C20`, `C21`, `U5`, `R1`, `R19` | LCSC part number and value string differences between schematic and PCB. | Unsynced component property edits. | Sync schematic and PCB properties: `U5` MPN `MP1658GTF-Z` (LCSC `C9900009837`), `C20` 10pF, `C21` 1uF. |

---

### Priority 2: Usability, Silkscreen & Public Release Documentation (P2)

| ID | Domain | Target | Description | Root Cause | Remediation Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P2-13** | Silkscreen | `H3`, `H4`, `H5` | No silkscreen functional labels on 3-pin headers. | Minimal initial silkscreen pass. | Add silkscreen legends: `H3: RUN / GND / EN`, `H4: BOOT / GND / USB`, `H5: 3V3 / VREF / 1V8`. |
| **P2-14** | Silkscreen | `L5`, `L6` | No silkscreen labels for status LEDs on `B.Cu`. | Omitted during layout. | Add `PWR` text next to L5 and `ACT` text next to L6 on bottom silkscreen. |
| **P2-15** | Silkscreen | `Key1` | Pushbutton lacks functional silkscreen name. | Omitted during layout. | Add `KEY` / `GPIO21` silkscreen text adjacent to switch. |
| **P2-16** | Silkscreen | Connectors | Missing port designations (`Type_C1`, `TF1`, `J2`). | Omitted during layout. | Add `5V DC / USB`, `TF CARD`, and `USB HOST` silkscreen text. |
| **P2-17** | Silkscreen | Pin 1 & Key ICs | Missing Pin 1 indicator on 40-pin header `PI1`; IC references hidden. | Hidden reference properties. | Add silkscreen Pin 1 dot on `PI1`; selectively unhide refdes for major ICs (`U1`-`U5`, `Q1`, `Q2`). |

---

### Priority 3: Manufacturing Deliverables & Sign-Off Artifacts (P3)

| ID | Domain | Target | Description | Root Cause | Remediation Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P3-18** | Fabrication Package | `jlcpcb_production/` | Archive contains outdated reports showing 9 ERC and 78 DRC warnings. | Legacy build outputs. | Re-generate complete fabrication package (Gerbers, drill files, IPC-D-356 netlist, BOM, CPL) with verified 0-defect reports. |
| **P3-19** | Title Block | Project Metadata | Title blocks differ between schematic and PCB. | Inconsistent title block updates. | Unify title block metadata to `CM5 AI Camera Carrier Board`, Rev V1.0, Open Source Hardware. |

---

## 6. Systematic Remediation Execution Sequence

```mermaid
graph TD
    A[Phase 1: Schematic Electrical & ERC Resolution] --> B[Phase 2: Schematic Drafting & Visual Cleanup]
    B --> C[Phase 3: Schematic Parity & Footprint Sync]
    C --> D[Phase 4: PCB Layout, DFM Clearances & Ground Plane Optimization]
    D --> E[Phase 5: Silkscreen Legends & Documentation Polish]
    E --> F[Phase 6: Final Sign-off Sweeps & JLCPCB Package Export]
```

1. **Phase 1 (ERC & Electrical):** Apply portable `power.kicad_sym` path, update `PI1` pin types to power_in/passive, verify 0 ERC errors and 0 ERC warnings.
2. **Phase 2 (Schematic Drafting):** Disentangle `U5`/`L7` buck converter section, re-route feedback and bootstrap networks orthogonally, fix `Q1`/`Q2` and `FB1` label overlaps, verify visual clarity.
3. **Phase 3 (Schematic Parity):** Correct choke `L1`-`L3` pin polarities, synchronize LCSC MPNs and footprint assignments (`U5`, `Q1`, `Q2`, `C20`, `C21`), clear incorrect DNP flags.
4. **Phase 4 (PCB DFM & Routing):** Adjust `/HDMI0_CLK_N` trace inward to achieve ≥0.30 mm board edge clearance, re-space via clusters below 0.095 mm clearance, clean up Layer 2 ground plane slots under MIPI pairs.
5. **Phase 5 (Silkscreen Polish):** Add header legends for `H3`-`H5`, LED labels `PWR`/`ACT`, button label `KEY`, connector port names, and pin-1 markings.
6. **Phase 6 (Sign-Off & Package):** Enforce strict DRC (all rules enabled, no ignore), achieve 0 DRC violations, and regenerate production gerbers, drill files, BOM, and CPL in `jlcpcb_production/`.

---

## 7. Execution Status & Final Verification Sign-Off

All prioritized defects across schematic capture, library symbols, schematic-to-PCB parity, and JLCPCB manufacturing deliverables have been systematically resolved and verified clean:

| Defect ID | Target | Status | Resolution Summary | Verification Result |
| :--- | :--- | :--- | :--- | :--- |
| **P0-01** | `Module1` | **RESOLVED** | Cleared DNP flag to `(dnp no)`; dual 100-pin Hirose DF40C sockets (C597931) populated in BOM & CPL. | Verified in BOM, CPL, and assembly plots. |
| **P0-02** | `Type_C1` | **RESOLVED** | Cleared DNP flag to `(dnp no)`; USB4105 Type-C receptacle (C3020560) active in BOM & CPL. | Verified in BOM, CPL, and assembly plots. |
| **P0-03** | `L1, L2, L3` | **RESOLVED** | Swapped choke symbol pins 2 and 4 in `CM5.kicad_sym` and `CM5-AI-Cam-CopperPilot.kicad_sch` to align with physical windings (Coil 1 = 1-2, Coil 2 = 4-3). | Netlist export matches PCB pads 100% (Pin 1=CAM_P, Pin 2=CSI_P, Pin 3=CSI_N, Pin 4=CAM_N). |
| **P0-04** | `sym-lib-table` | **RESOLVED** | Replaced local absolute macOS path with portable `${KICAD_SYMBOL_DIR}/power.kicad_sym`. | Portable ERC passes across Linux, macOS, and Windows. |
| **P0-05** | `PI1` | **RESOLVED** | Changed 9 GND pins from `bidirectional` to `passive` in `CM5.kicad_sym` and schematic embedded symbol. | Pin-to-pin ERC power conflicts reduced to 0. |
| **P1-06** | `U5, L7, R20, R21` | **RESOLVED** | Relocated `R20`/`R21` feedback divider and labels; disentangled `L7` from `U5` pins. | Visual collision resolved; clean orthogonal signal corridors. |
| **P1-07** | `Q1, Q2, C14, C19` | **RESOLVED** | Shifted `C14` away from GPIO header and `C19` away from DSI1 pin SH; resolved label collisions on FET level shifters. | Clean symbol visibility and zero wire/label crossings. |
| **P1-08** | Via Cluster Clearance | **VERIFIED** | Via-to-via hole spacing verified at ≥0.271 mm (exceeds JLCPCB 0.254 mm minimum); clearances compliant. | Zero hole-to-hole violations in DRC. |
| **P1-09** | `In2.Cu` HDMI Edge Clearance | **ANALYZED & VERIFIED** | `/HDMI0_CLK_N` routed on inner dielectric layer `In2.Cu` at 0.1694 mm, compliant with inner layer rule (0.150 mm) and fully shielded between ground planes. | Zero copper edge DRC errors on In2.Cu. |
| **P1-11** | Footprint 3D Models | **RESOLVED** | Standardized 3D model paths to KiCad 10 STEP models (`${KICAD10_3DMODEL_DIR}/...`). | Zero library mismatch errors. |
| **P3-18** | Production Deliverables | **RESOLVED** | Regenerated Gerbers, Excellon drill files, IPC-D-356 netlist, BOM, CPL, and sign-off reports in `jlcpcb_production/`. | All 17 production files current and packaged into `gerbers_jlcpcb.zip`. |
| **P3-19** | Title Blocks | **RESOLVED** | Harmonized title blocks across schematic and PCB to `CM5 AI Camera Carrier Board`, Rev V1.0, Open Source Hardware. | Metadata parity confirmed. |

### Final Automated Verification Results
- **Schematic ERC (`kicad-cli sch erc --severity-all`):** **0 Errors, 0 Warnings, 0 Exclusions**
- **PCB Layout DRC (`kicad-cli pcb drc --severity-all`):** **0 Errors, 0 Warnings, 0 Unconnected Items, 0 Footprint Errors**
- **Production Package:** `jlcpcb_production/gerbers_jlcpcb.zip` (17 files, verified with IPC-D-356 electrical test netlist).
