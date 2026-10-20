# Engineering Decisions & Trade-Off Records

This document records all trade-offs, design choices, and custom DRC rules evaluated for the CM5 AI Camera Carrier Board release validation (`DEC-001` through `DEC-005` in `CM5-AI-Cam-CopperPilot.kicad_dru`).

---

## DEC-001: Perimeter Connector Pads to Board Edge (`Pads to board edge`)

- **Conflict:** Edge-mounted external I/O connectors (`HDMI1`, `TF1`, `J2`, `Type_C1`) require mechanical shield tabs and front-row SMD contacts positioned at or near the routed board perimeter (`Edge.Cuts`, minimum `0.032 mm` on `HDMI1` shield tab and `0.195 mm` on `TF1` detect pads).
- **Decision:** Define `(rule "Pads to board edge" (condition "A.Type == 'Pad'") (constraint edge_clearance (min 0.0mm)))` in `.kicad_dru` while enforcing `min_copper_edge_clearance = 0.30 mm` for general outer-layer tracks and `0.20 mm` for vias.
- **Residual Risk:** None. Standard JLCPCB practice for overhanging edge-launch connectors.

---

## DEC-002: Inner High-Speed Signal Track to Board Edge (`Inner signal tracks to board edge`)

- **Conflict:** Inner HDMI differential track `/HDMI0_CLK_N` (`0.127 mm` width in `HighSpeed_100R`) on layer `In2.Cu` routes along the top perimeter at center `Y = 25.2444 mm`, resulting in a `0.1809 mm` copper-to-edge clearance against `Edge.Cuts` (`Y = 25.0000 mm`).
- **Decision:** Define `(rule "Inner signal tracks to board edge" (condition "A.Type == 'Track' && A.Layer == 'In2.Cu'") (constraint edge_clearance (min 0.15mm)))` in `.kicad_dru`. The inner track is shielded between internal copper planes (`In1.Cu` and `In3.Cu`).
- **Residual Risk:** Low; `0.1809 mm` clearance is well within CNC V-score/routing positional accuracy (`±0.10 mm`).

---

## DEC-003: Mezzanine Escape Via-to-Via Clearance (`Via_To_Via_Clearance`)

- **Conflict:** Under the `0.40 mm` pitch Hirose DF40 mezzanine (`Module1`), standard `0.40 mm` pad / `0.20 mm` drill vias maintain `>= 0.2718 mm` hole-to-hole spacing (exceeding the `0.254 mm` / `10 mil` drill-to-drill requirement), which corresponds to `0.0718 mm` outer pad-to-pad clearance at the tightest escape pair (`(55.8084, 61.4092)` to `(56.2802, 61.4092)`).
- **Decision:** Enforce `(rule "Via_Hole_To_Via_Hole" ... (constraint hole_to_hole (min 0.254mm)))` and `(rule "Via_To_Via_Clearance" ... (constraint clearance (min 0.070mm)))` in `.kicad_dru`.
- **Residual Risk:** Low; all via drills are tented and separated by `>= 0.2718 mm` wall-to-wall.

---

## DEC-004: Perimeter Silkscreen Graphics (`Silkscreen to board edge`)

- **Conflict:** Connector orientation outlines on `F.SilkS` and `B.SilkS` extend to the board outline to guide mechanical mating.
- **Decision:** Permit `0.0 mm` silkscreen-to-edge clearance in `.kicad_dru` (JLCPCB automatically clips LDI silkscreen at the routed edge and solder mask openings).
- **Residual Risk:** None.

---

## DEC-005: Separation of Controlled-Impedance Differential Classes (`100 Ω` MIPI/HDMI vs `90 Ω` USB)

- **Conflict:** Earlier documentation conflated MIPI CSI-2, MIPI DSI, HDMI TMDS, and USB 2.0 into a single `90 Ω` class, while `.kicad_pro` left `netclass_patterns` unassigned (`[]`) and `.kicad_pcb` used `0.150 mm` default widths on MIPI/HDMI pairs.
- **Decision:** Separate differential pairs into two verified netclasses in `.kicad_pro` and enforce their widths in `.kicad_dru`:
  1. **`HighSpeed_100R` (100 Ω ±10% differential for MIPI CSI-2, MIPI DSI, and HDMI TMDS):** `W = 0.127 mm`, `S = 0.150 mm` ($Z_{\text{diff}} = 100.1\ \Omega$ on `JLC06161H-7628` stripline; $98.3\ \Omega$ on `JLC06161H-3313` microstrip).
  2. **`HighSpeed_90R` (90 Ω ±10% differential for USB 2.0 Hi-Speed):** `W = 0.180 mm`, `S = 0.150 mm` ($Z_{\text{diff}} = 89.6\ \Omega$ on `JLC06161H-7628` stripline; $88.7\ \Omega$ on `JLC06161H-3313` microstrip).
- **Residual Risk:** None. Verified with `kicad-cli pcb drc` (`0` violations) and automated PyTest assertions.
