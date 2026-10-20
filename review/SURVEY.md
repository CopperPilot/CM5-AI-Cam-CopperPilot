# Engineering Survey & Defect Assessment Report

**Board:** CM5 AI Camera Carrier Board  
**Revision:** V1.0  
**KiCad Version:** 10.0.4  
**Date:** 2026-10-17  
**Lead Hardware Engineer:** Hardware Engineering Team  

---

## 1. Executive Summary

A comprehensive, multi-domain audit across differential impedance control, stackup synchronization, schematic electrical correctness, PCB layout, DFM rules, BOM/CPL sourcing, and library hygiene was performed on the design.

### Issue Counts by Severity & Domain

| Severity | Count | Meaning |
|---|---|---|
| **P0 — Blocker** | 4 | Unassigned 100 Ω / 90 Ω differential netclasses & widths (`IMP-001`); `C20` 0.1 µF shorting 24 MHz MCLK & critical LCSC mismatches on `R20, U3, U5, HDMI1, L1–L3` (`SCH-004`); `Type_C1` DNP override (`PCB-001`); custom DRC rules (`DFM-001`) |
| **P1 — Major** | 13 | Inner/bottom layer 100 Ω MIPI/HDMI width updates (`IMP-002..006`); schematic netclass pattern assignments (`IMP-007`); `DSI1` symbol parity (`SCH-001`); `C19/R36` DNP flags (`PCB-002, PCB-003`); `Q1/Q2/U5` footprints (`PCB-004, PCB-005`); `U4/U7, C20, C21` parity (`PCB-006..008`) |
| **P2 — Minor** | 6 | `U6` package suffix `FSUSB42UMX` (`SCH-005`); `R1, R19, J2` LCSC synchronization (`SCH-002, SCH-003, PCB-009`); release collateral & impedance docs (`DOC-001`) |
| **P3 — Polish** | 1 | `Module1` description metadata parity (`PCB-010`) |
| **Total Tracked** | **24** | All 24 issues cataloged with root cause, remediation, and verification criteria |

### Final DRC / ERC Status
- **ERC Violations:** 0 Errors, 0 Warnings
- **DRC Violations:** 0 Errors, 0 Warnings, 0 Unconnected Items
- **Schematic Parity Issues:** 0 Footprint / Symbol Mismatches

---

## 2. Key Technical Remediations

1. **Separation of 100 Ω (MIPI/HDMI) and 90 Ω (USB) Differential Classes (`IMP-001..007`):**
   - Configured and assigned `HighSpeed_100R` (`W = 0.127 mm, S = 0.150 mm`, yielding $Z_{\text{diff}} = 100.1\ \Omega$ on `JLC06161H-7628` stripline and $98.3\ \Omega$ on `JLC06161H-3313` microstrip) for all 26 MIPI CSI-2, MIPI DSI, and HDMI TMDS differential nets.
   - Configured and assigned `HighSpeed_90R` (`W = 0.180 mm, S = 0.150 mm`, yielding $Z_{\text{diff}} = 89.6\ \Omega$ on `JLC06161H-7628` stripline and $88.7\ \Omega$ on `JLC06161H-3313` microstrip) for all 8 USB 2.0 Hi-Speed differential nets.
   - Synchronized `.kicad_pcb` dielectric thicknesses with `JLC06161H-7628` (`0.2104 mm` prepreg, `0.4000 mm` core, $\varepsilon_r = 4.6$) and enforced `HighSpeed_100R_Impedance_Width` and `HighSpeed_90R_Impedance_Width` in `.kicad_dru`.
2. **24 MHz Camera Clock & Critical BOM Part Number Remediation (`SCH-004`, `SCH-005`, `PCB-007`, `PCB-008`):**
   - Restored `C20` on the 24 MHz `/MCLK` line from `0.1 µF` (`fc = 72.3 kHz`, which attenuated the 24 MHz clock) to **`10 pF` (`C32949`, $f_c = 723\text{ MHz}$)**.
   - Corrected critical LCSC part mappings across schematic, PCB, and `bom_jlcpcb.csv`: `R20` (`61.9 kΩ` $\to$ `C25803`), `U3` (`RT9013-12` 1.2V LDO $\to$ `C47773`), `U1` (`RT9193-28GB` 2.8V LDO $\to$ `C15075`), `U5` (`MP1658GTF-Z` $\to$ `C2960187`), `HDMI1` (`Molex 47151-0001` $\to$ `C424662`), `L1–L3` (`MCF1210BF2-900T01` 1.2×1.0 mm chokes $\to$ `C110443`), `C21` (`330 pF` $\to$ `C1534`), and `U6` (`FSUSB42UMX` `C11145`).
   - Excluded DNP configuration straps `R31, R32, R33` from `bom_jlcpcb.csv` and `cpl_jlcpcb.csv` (`--exclude-dnp`) so active-low `WL_nDisable` and `BT_nDisable` remain enabled.
3. **Footprint Library & 3D Path Hygiene:**
   - Repaired missing pad `(at ±0.51 0)` coordinates in `CM5.pretty/R_0402_1005Metric.kicad_mod`, updated `TF1` attribute to `smd`, and standardized all `.kicad_pcb` 3D model paths to `${KIPRJMOD}`.

---

## 3. JLCPCB Constraint Compliance Summary

| Constraint | Design Value | JLC 6-Layer Limit | Compliance Status |
|---|---|---|---|
| `HighSpeed_100R` trace / gap (MIPI, HDMI) | `0.127 mm / 0.150 mm` (`100.1 Ω`) | `0.090 mm / 0.090 mm` | **Compliant (Enforced in DRU)** |
| `HighSpeed_90R` trace / gap (USB 2.0) | `0.180 mm / 0.150 mm` (`89.6 Ω`) | `0.090 mm / 0.090 mm` | **Compliant (Enforced in DRU)** |
| General signal track width | `0.150 mm` (`0.180 mm` 50 Ω clocks) | `0.090 mm` | **Compliant** |
| Via drill / pad diameter | `0.20 mm / 0.40 mm` | `0.15 mm / 0.25 mm` | **Compliant** |
| Via hole-to-hole spacing | `>= 0.2718 mm` (DRU min `0.254 mm`) | `0.200 mm` (`0.254 mm` std) | **Compliant (`DEC-003`)** |
| Inner track to board edge (`In2.Cu`) | `0.1809 mm` (DRU min `0.150 mm`) | `0.150–0.200 mm` | **Documented (`DEC-002`)** |
