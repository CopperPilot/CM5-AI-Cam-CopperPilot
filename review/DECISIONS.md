# Engineering Decisions & Trade-Off Records

This document records all trade-offs, design choices, and waivers evaluated for the CM5 AI Camera Carrier Board release validation.

---

## DEC-001: Via-to-Via Clearance & GND Via Nudge (DFM-001)

- **Conflict:** A GND via at `(55.8084, 61.4092)` on layer `B.Cu` was spaced 0.4718 mm center-to-center from adjacent `/SD_PWREN` signal via `(56.2802, 61.4092)`, resulting in a 0.0718 mm copper clearance. A legacy custom rule in `.kicad_dru` permitted `clearance (min 0.070mm)`, which was below JLCPCB standard manufacturing targets (min 0.150 mm).
- **Options Considered:**
  1. *Option A (Waiver):* Waive the violation and retain the 0.070 mm clearance rule. (Rejected: violates Section 3 constraint rule forbidding rule relaxation below JLCPCB targets).
  2. *Option B (Reroute signal):* Reroute `/SD_PWREN` trace and via across In3.Cu/B.Cu. (Rejected: introduces unnecessary signal topology changes).
  3. *Option C (Nudge GND via):* Nudge the GND via by 0.158 mm to `(55.6500, 61.4092)`. Both vias remain centered on solid ground and routing channels; clearance expands to 0.180 mm, well above the 0.150 mm target. (Selected).
- **Decision:** Adopt Option C. Move GND via to X=55.65 mm and update `.kicad_dru` to enforce JLCPCB standard minimum clearance >= 0.150 mm.
- **Priority Rule Applied:** Manufacturability / Yield > Cost > Aesthetics.
- **Residual Risk:** None. Verified with full DRC and zero unconnected items.
- **Approved By:** Lead Hardware Engineer.

---

## DEC-002: DSI Display Connector Shield Pin / Pad Mapping (SCH-001)

- **Conflict:** DSI 15-pin FPC connector `DSI1` symbol pin 16 was designated `SH` (Shield / GND), while the physical footprint `Molex_200528-0150_1x15-1MP_P1.00mm_Horizontal` has mechanical side mounting tabs named `MP`. This produced a DRC `[net_conflict]: No pad found for pin SH (GND) in schematic`.
- **Options Considered:**
  1. *Option A:* Rename footprint pads to `SH`. (Rejected: modifies vendor footprint library naming).
  2. *Option B:* Update schematic symbol pin 16 number to `MP` and connect to GND net. (Selected: matches KiCad connector convention and directly maps to physical pads).
- **Decision:** Adopt Option B.
- **Priority Rule Applied:** Functional Correctness & Parity.
- **Residual Risk:** None. Side mounting brackets are securely grounded for EMI shielding.
- **Approved By:** Lead Hardware Engineer.

---

## DEC-003: Harmonization of Alternate MPNs (PCB-006, PCB-007, PCB-008)

- **Conflict:** Several PCB footprint properties had been edited with second-source or test values (`DIO7003HCST5` on U4/U7, `10pF` on C20, `1uF` on C21), conflicting with the primary schematic and JLCPCB production BOM.
- **Decision:** Synchronize all footprint values and LCSC part numbers on the PCB directly to match the verified schematic and JLCPCB assembly BOM (`STMPS2171STR`, `0.1uF C1525`, `330pF C1547`).
- **Priority Rule Applied:** Manufacturability & Parity.
- **Residual Risk:** None.
- **Approved By:** Lead Hardware Engineer.
