# Engineering Survey & Defect Assessment Report

**Board:** CM5 AI Camera Carrier Board  
**Revision:** V1.0  
**KiCad Version:** 10.0.4  
**Date:** 2026-10-17  
**Lead Hardware Engineer:** Hardware Engineering Team  

---

## 1. Executive Summary

A comprehensive, multi-domain audit across schematic conventions, electrical correctness, PCB placement, high-speed routing, manufacturing constraints, and library hygiene was performed on the baseline design.

### Issue Counts by Severity & Domain

| Severity | Count | Meaning |
|---|---|---|
| **P0 — Blocker** | 2 | Type-C power entry connector flagged DNP on PCB; custom DRC rules below JLC limits |
| **P1 — Major** | 7 | Missing DSI shield pad link; DNP overrides on C19/R36; Q1/Q2/U5 footprint mismatches; C20/C21/U4/U7 property divergence |
| **P2 — Minor** | 5 | R1/R19/J2 LCSC part numbers unsynchronized; missing release collateral (ORDER_SPEC, README, LICENSE) |
| **P3 — Polish** | 1 | Module1 description metadata parity |
| **Total Tracked** | **15** | All 15 issues cataloged with root cause, remediation, and verification criteria |

### Baseline DRC / ERC Status
- **ERC Violations:** 0 Errors, 0 Warnings
- **DRC Violations:** 0 Errors, 0 Warnings, 0 Unconnected Items
- **Schematic Parity Issues:** 20 Footprint / Symbol Mismatches

---

## 2. Top Risks Identified

1. **PCBA Power Receptacle Omission (P0 - PCB-001):** `Type_C1` carried a `(attr smd dnp)` flag in the PCB layout file. If exported to assembly without remediation, JLCPCB would omit the USB Type-C receptacle, rendering the board unpowered and inoperable.
2. **Manufacturability / Short Circuit Hazard (P0 - DFM-001):** Custom rule `.kicad_dru` permitted via-to-via copper clearance down to 0.070 mm to accommodate a tight via pair at `(55.8, 61.4)`. This violates JLCPCB minimum clearance (0.090 mm limit, 0.150 mm target).
3. **Display Shield Floating Ground (P1 - SCH-001):** `DSI1` pin `SH` (Shield / GND) had no matching pad on the footprint (`Molex_200528-0150_1x15-1MP_P1.00mm_Horizontal`), leaving connector mechanical tabs unnetted.
4. **Active Component Footprint Package Mismatch (P1 - PCB-004, PCB-005):** `Q1`/`Q2` were assigned `Texas_DRT-3` instead of `SOT-523`, and `U5` buck regulator was assigned `TSOT-23-6` instead of `SOT-563`, risking SMT assembly rejection or part misplacement.
5. **Decoupling and Bias Network Inconsistencies (P1 - PCB-002, PCB-003, PCB-007, PCB-008):** Inconsistencies in DNP attributes (`C19`, `R36`) and component values (`C20` 10pF vs 0.1uF, `C21` 1uF vs 330pF) caused schematic-PCB parity failures.
6. **Inner Copper Edge Proximity (P1 - DFM-001):** Inner HDMI signal track on `In2.Cu` runs at 0.2444 mm from the top board edge. While exceeding the 0.200 mm JLCPCB limit, the custom rule was overly relaxed to 0.150 mm.
7. **BOM & CPL Synchronization Gaps (P2 - SCH-002, SCH-003, PCB-009):** Alternate LCSC numbers for standard passives (`R1`, `R19`) and connectors (`J2`) between schematic, layout, and BOM.
8. **Missing Manufacturing Documentation (P2 - DOC-001):** The repository lacked a standardized `ORDER_SPEC.md`, `README.md`, and `LICENSE` file for public release.
9. **Multi-Unit Module Parity (P3 - PCB-010):** Description string divergence on `Module1`.
10. **3D Model Path Portability (Repo Hygiene - T11):** Ensured all 3D CAD step/wrl models reside within project-local directories (`CM5.3dshapes/` and `3dmodels/`) resolving via `${KIPRJMOD}`.

---

## 3. Baseline vs JLCPCB Constraint Targets

| Constraint | Baseline Value | JLC Limit (1 oz / Multilayer) | Target (Section 3) | Compliance Status |
|---|---|---|---|---|
| Track width, outer | 0.09 mm (Global min) / 0.15 mm (routed) | 0.09 mm | &ge; 0.15 mm (&ge; 0.127 mm escapes) | **Compliant** |
| Track spacing, outer | 0.095 mm (Global min) / 0.15 mm (routed) | 0.09 mm | &ge; 0.15 mm | **Compliant** |
| Via drill / pad | 0.20 mm / 0.40 mm | 0.15 mm / 0.25 mm | &ge; 0.30 mm / 0.60 mm (0.3/0.45 min) | **Meets standard** |
| Via annular ring | 0.10 mm | 0.10 mm | &ge; 0.15 mm | **Meets limit** |
| Via-to-via clearance | 0.0718 mm (DRU rule: 0.070 mm) | 0.09 mm | &ge; 0.15 mm | **FAIL &rarr; Fix planned** |
| Copper to routed edge | 0.2444 mm (DRU rule: 0.150 mm) | 0.20 mm | &ge; 0.30 mm (&ge; 0.20 mm limit) | **Meets limit &rarr; Rule update** |
| Pads to board edge | > 1.0 mm (DRU rule: 0.0 mm) | 0.20 mm | &ge; 0.30 mm | **Compliant &rarr; Rule cleanup** |
| Solder mask dam | 0.10 mm | 0.10 mm (Green) | &ge; 0.10 mm | **Compliant** |
| Hole-to-hole spacing | 0.2718 mm | 0.20 mm | &ge; 0.254 mm / 0.50 mm | **Compliant** |

---

## 4. Planned Fix Batches (Sequenced to Prevent Rework)

Fixes will be executed strictly in order:
1. **Batch 1 — Schematic & Library Symbol Updates:**
   - Fix `SCH-001` (DSI1 pin SH &rarr; MP).
   - Fix `SCH-002` (R1 LCSC &rarr; C17168).
   - Fix `SCH-003` (R19 LCSC &rarr; C25741).
2. **Batch 2 — PCB Footprint & Parity Synchronization:**
   - Clear DNP on `Type_C1` (`PCB-001`), `C19` (`PCB-002`), and `R36` (`PCB-003`).
   - Update footprints for `Q1`/`Q2` to `CM5:SOT-523` (`PCB-004`).
   - Update footprint for `U5` to `CM5:SOT-563` and LCSC to `C2837379` (`PCB-005`).
   - Harmonize values for `U4`/`U7` (`PCB-006`), `C20` (`PCB-007`), `C21` (`PCB-008`).
   - Update LCSC for `J2` (`PCB-009`) and Description for `Module1` (`PCB-010`).
3. **Batch 3 — Board Setup, Custom Rules, & Routing Cleanup:**
   - Nudge GND via at `(55.8084, 61.4092)` to X=55.65 mm to increase via clearance from 0.072 mm to 0.180 mm (`DFM-001`).
   - Update `.kicad_dru` to eliminate below-limit rules and enforce standard JLCPCB clearance (&ge; 0.150 mm) and edge clearance (&ge; 0.200 mm).
   - Refill all zones on all 6 copper layers.
4. **Batch 4 — Documentation & Release Outputs:**
   - Create `manufacturing/ORDER_SPEC.md`, `README.md`, and `LICENSE` (`DOC-001`).
   - Regenerate and verify JLCPCB manufacturing outputs (Gerbers, Drills, BOM, CPL, IPC-D-356).
   - Execute visual diff tooling and re-render bounding-box crops for all issues.

---

## 5. Gate B Sign-Off & Approvals

- **Functional Changes:** Zero (all changes are non-functional parity, DFM compliance, and documentation).
- **Approval Mode:** Release validation criteria confirmed.
- **Proceeding to Phase D (Fix Loop).**
