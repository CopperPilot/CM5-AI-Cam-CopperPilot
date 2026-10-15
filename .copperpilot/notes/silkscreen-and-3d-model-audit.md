# Silkscreen and 3D Model Audit Report
**Board:** CM5 AI Camera Carrier Board (`CM5-AI-Cam-CopperPilot.kicad_pcb`)  
**EDA Version:** KiCad 10.0.3 (macOS arm64)  
**Date:** 2026-10-15  
**Sign-off Standard:** JLCPCB 6-Layer Standard Process (`JLC06161H-3313`)

---

## 1. Silkscreen Defect & Text Audit

### 1.1 DRC Violation Breakdown (571 Total Warnings)
A total of 571 DRC violations exist in the uncorrected board file. Silkscreen-related warnings account for 473 violations (82.8% of all DRC issues). An additional 90 violations correspond to unassigned library linkages (`lib_footprint_issues`).

| DRC Warning Type | Count | Root Cause Mechanism |
| :--- | :---: | :--- |
| `silk_overlap` | 199 | 195 caused by visible 1.27 mm LCSC text strings colliding across adjacent SMD components; 4 caused by tight 0402 passive silkscreen outlines (0.12–0.14 mm clearance vs 0.15 mm rule). |
| `silk_over_copper` | 199 | 172 caused by visible 1.27 mm LCSC text placed at component origin `(0, 0)` directly over solder pads; 25 caused by HDMI1 connector silkscreen outline cutting across SMD/shield pads; 1 caused by board title text clipping C23 pad 2; 1 caused by Module1 arc clipping HDMI1 shield pad. |
| `lib_footprint_issues` | 90 | Footprint library `CM5` registered with absolute host path `/Users/adityang/...` instead of portable `${KIPRJMOD}/CM5.pretty`. |
| `nonmirrored_text_on_back_layer` | 54 | All 54 footprints placed on bottom copper (`B.Cu`) have their visible `LCSC` property on `B.SilkS` missing `(justify mirror)`. |
| `silk_edge_clearance` | 18 | 5 caused by oversized LCSC text crossing the 0.15 mm edge margin; 8 caused by Module1 board-edge silkscreen boundary on `B.SilkS`; 3 caused by DSI1 connector (0.03 mm to edge); 2 caused by HDMI1 corner arc. |
| `via_dangling` | 6 | Unconnected or single-layer test/ground vias. |
| `text_thickness` | 3 | Board text `CM5 AI Camera Carrier Board` (insufficient TrueType stroke weight), J1 Reference (0.12 mm < 0.15 mm min), J1 pin text "3" (0.12 mm < 0.15 mm min). |
| `track_dangling` | 2 | Unconnected stub tracks on net `/MP1658_BST`. |

*Experimental Verification:* Setting `(hide yes)` across all 90 `LCSC` properties immediately drops total DRC violations from 571 to 145:
- `nonmirrored_text_on_back_layer` drops from 54 to **0** (-100%)
- `silk_overlap` drops from 199 to **4** (-98.0%)
- `silk_over_copper` drops from 199 to **27** (-86.4%)
- `silk_edge_clearance` drops from 18 to **13** (-27.8%)

---

### 1.2 The LCSC Property Defect
All 90 footprints in `CM5-AI-Cam-CopperPilot.kicad_pcb` contain a custom footprint property named `LCSC` (holding part numbers like `C25900`, `C25765`, `C3020560`).

- **Visibility:** 90 of 90 are **visible** (`hide yes` is omitted).
- **Placement Coordinates:** Placed at footprint origin `(at 0 0 0)` with rotation `0`.
- **Layer Allocation:** Placed on `F.SilkS` for top components (36 footprints) and `B.SilkS` for bottom components (54 footprints).
- **Typography:** Font size is `1.27 mm x 1.27 mm`, stroke thickness is `0.15 mm`.
- **Defect Impact:** A 6-to-8 character string (e.g. `C3020560`) rendered at 1.27 mm height spans approximately 7.5 mm to 9.5 mm in width. On 0402 passives (body size 1.0 mm x 0.5 mm) and fine-pitch ICs, this text blankets the solder pads and extends into neighboring components, triggering widespread solder-mask clearance clipping and text collisions in both DRC and the 3D viewer.
- **Back-Layer Mirroring Defect:** None of the 54 `LCSC` properties on `B.SilkS` have the `justify mirror` attribute. In KiCad, silkscreen text on back layers must be mirrored so that it reads legibly from the rear side; unmirrored text produces a `[nonmirrored_text_on_back_layer]` DRC warning for every single bottom component.

---

### 1.3 Reference Designator Text Audit
- **Total Footprints:** 90
- **Visible Reference Designators:** Only 1 footprint (`J1`, camera connector) has its Reference designator visible (`at -10.5 -7.2 0`, layer `F.SilkS`, font size `0.8 mm x 0.8 mm`, thickness `0.12 mm`).
- **Hidden Reference Designators:** 89 of 90 footprints have `(hide yes)` on their Reference designator.
- **Text Sizing & Thickness:** All 90 Reference properties are configured with size `0.8 mm x 0.8 mm` and stroke thickness `0.12 mm`.
- **JLCPCB Non-Compliance:** JLCPCB specifies a minimum silkscreen line thickness of `0.15 mm` (6 mil). Stroke thickness of `0.12 mm` violates the DRC setup constraint (`board setup constraints silk text thickness min thickness 0.1500 mm; actual 0.1200 mm`). If Reference designators are made visible for assembly inspection, their thickness must be increased from `0.12 mm` to `0.15 mm`.

---

### 1.4 Silkscreen Collision Hotspots & Edge Clipping
1. **HDMI1 Connector (Molex Mini-HDMI 47151-0001):**
   - Generates 25 `silk_over_copper` warnings.
   - Footprint silkscreen bounding box segments (`start 37.0 26.02`, `end 37.0 33.02` and `start 22.0 33.02`) intersect all 19 SMD signal pads (Pads 1–19) and shield PTH pads.
   - Generates 2 `silk_edge_clearance` warnings at the top-left board radius (`Arc on Edge.Cuts @ 24.5, 28.0`).
2. **Buck Converter U5 Cluster (MP1658GTF-Z):**
   - High component density around U5 generates 4 persistent `silk_overlap` warnings between passive silkscreen outlines:
     - `R36` vs `C27` (clearance 0.140 mm)
     - `R35` vs `R36` (clearance 0.120 mm)
     - `C24` vs `R20` (clearance 0.140 mm)
     - `R16` vs `C21` (clearance 0.140 mm)
3. **Board Edge Clipping (13 Non-LCSC Warnings):**
   - `DSI1` (Molex 200528-0150 15-pin FFC): Outline segments sit 0.03 mm from the top Edge.Cuts route (`y = 25.0 mm`), violating the 0.15 mm silk-to-edge constraint.
   - `Module1` (Compute Module 5): 8 perimeter arc and segment warnings along Edge.Cuts (actual clearance 0.00 mm to 0.14 mm) due to silkscreen silkscreen outline duplicating the board edge.
4. **Board Title Text:**
   - Free text `CM5 AI Camera Carrier Board` at `(37.5, 62.5)` overlaps Pad 2 of capacitor `C23` (`56.0, 62.52`) and triggers `text_thickness` due to TrueType font rendering.

---

### 1.5 JLCPCB-Compliant Silkscreen Parameter Recommendations
To achieve 100% compliance with JLCPCB fabrication capabilities:
1. **Hide LCSC Properties:** Add `(hide yes)` to the `LCSC` property on all 90 footprints in the board and schematic. LCSC C-numbers belong in BOM metadata, not silkscreen printing.
2. **Reference Designator Sizing:**
   - Minimum Height: `0.80 mm` (recommended `1.00 mm` for clear legibility).
   - Minimum Width: `0.80 mm` (recommended `1.00 mm`).
   - Line Thickness: `0.15 mm` (6.0 mil) minimum; update all existing `0.12 mm` text to `0.15 mm`.
   - Back Layer Justification: Any visible text on `B.SilkS` must include `(justify mirror)`.
3. **HDMI1 Silkscreen Trim:** Remove or pull back the interior footprint silkscreen lines on `CM5:HDMI_Mini-C_Molex_47151-0001` so they remain at least `0.15 mm` outside solder mask openings.
4. **Board Title Relocation:** Move `CM5 AI Camera Carrier Board` away from `C23` and switch from system TrueType font to KiCad Hershey stroke font with `size 1.2 mm 1.2 mm`, `thickness 0.18 mm`.

---

## 2. 3D Model Audit

### 2.1 Complete 3D Model Inventory (90 Footprints)
All 90 footprints contain a `(model ...)` record. However, several paths are broken, unresolvable in KiCad 10, or using improper file formats.

| Footprint Ref(s) | Component Description | Current Configured Model Path | Format | Status in KiCad 10 | Recommended Fix Path |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **J2** | Molex Vertical USB-A Host | `${KIPRJMOD}/3dmodels/USB_A_Molex_105057-0001_Vertical.wrl` | VRML (.wrl) | **Fails export / mis-scaled:** Cannot export to STEP; coordinates in inches with 1:1 scale. | `${KIPRJMOD}/3dmodels/USB_A_Molex_105057-0001_Vertical.step` |
| **Type_C1** | GCT USB-C 16-Pin Receptacle | `${KICAD9_3DMODEL_DIR}/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step` | STEP | **Missing variable:** `${KICAD9_3DMODEL_DIR}` does not exist in KiCad 10. | `${KIPRJMOD}/CM5.3dshapes/USB4105-GF-A.step` (with `rotate -90 0 0`) |
| **H3, H4, H5** | 1x03 2.54mm Pin Headers | `${KICAD9_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x03_P2.54mm_Vertical.step` | STEP | **Missing variable:** `${KICAD9_3DMODEL_DIR}` unresolved. | `${KICAD10_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x03_P2.54mm_Vertical.step` |
| **FB1** | 0603 Ferrite Bead | `${KICAD9_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0603_1608Metric.step` | STEP | **Missing variable:** `${KICAD9_3DMODEL_DIR}` unresolved. | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0603_1608Metric.step` |
| **J1** | IMX219 30-Pin Camera | `./3dmodels/Camera_IMX219-D160.step` | STEP | **Brittle relative path:** Fails if CWD != project root. | `${KIPRJMOD}/3dmodels/Camera_IMX219-D160.step` |
| **HDMI1** | Mini-HDMI Connector | `./CM5.3dshapes/JTHDA-19F08.STEP` | STEP | **Brittle relative path:** Fails if CWD != project root. | `${KIPRJMOD}/CM5.3dshapes/JTHDA-19F08.STEP` |
| **TF1** | MicroSD Card Socket | `./CM5.3dshapes/5033981892.stp` | STEP | **Brittle relative path:** Fails if CWD != project root. | `${KIPRJMOD}/CM5.3dshapes/5033981892.stp` |
| **L7** | 4.7uH Power Inductor | `./CM5.3dshapes/SRP5030CC.stp` | STEP | **Brittle relative path:** Fails if CWD != project root. | `${KIPRJMOD}/CM5.3dshapes/SRP5030CC.stp` |
| **Module1** | Raspberry Pi CM5 | `./CM5.3dshapes/DF40C-100DS.stp` (x2), `./CM5.3dshapes/CM5.step` (x1) | STEP | **Brittle relative path:** Fails if CWD != project root. | `${KIPRJMOD}/CM5.3dshapes/DF40C-100DS.stp`, `${KIPRJMOD}/CM5.3dshapes/CM5.step` |
| **C1–C10, C12–C21, C23–C24, C27–C32** (26 pcs) | 0402 Capacitors | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` |
| **C11, C22, C25, C26, C4** (5 pcs) | 0805 Capacitors | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0805_2012Metric.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0805_2012Metric.step` |
| **R1–R5, R7–R8, R10–R17, R19–R22, R24, R28–R36** (29 pcs) | 0402 Resistors | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` |
| **DSI1** | 15-Pin FPC Connector | `${KICAD10_3DMODEL_DIR}/Connector_FFC-FPC.3dshapes/TE_1-84952-5_1x15-1MP_P1.0mm_Horizontal.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Connector_FFC-FPC.3dshapes/TE_1-84952-5_1x15-1MP_P1.0mm_Horizontal.step` |
| **PI1** | 40-Pin GPIO Header | `${KICAD10_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_2x20_P2.54mm_Vertical.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_2x20_P2.54mm_Vertical.step` |
| **Key1** | Push Button Switch | `${KICAD10_3DMODEL_DIR}/Button_Switch_SMD.3dshapes/SW_SPST_PTS645Sx43SMTR92.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Button_Switch_SMD.3dshapes/SW_SPST_PTS645Sx43SMTR92.step` |
| **L1, L2, L3** | Common Mode Chokes | `${KICAD10_3DMODEL_DIR}/Inductor_SMD.3dshapes/L_CommonModeChoke_Coilank_ACM1210.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Inductor_SMD.3dshapes/L_CommonModeChoke_Coilank_ACM1210.step` |
| **L5, L6** | 0603 LEDs | `${KICAD10_3DMODEL_DIR}/LED_SMD.3dshapes/LED_0603_1608Metric.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/LED_SMD.3dshapes/LED_0603_1608Metric.step` |
| **Q1, Q2** | SOT-523 / DRT-3 MOSFETs | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/Texas_DRT-3.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/Texas_DRT-3.step` |
| **U1, U2, U3, U4, U7, U8** (6 pcs) | SOT-23-5 Regulators / Switches | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23-5.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23-5.step` |
| **U5** | TSOT-23-6 Buck Converter | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/TSOT-23-6.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/TSOT-23-6.step` |
| **U6** | UMLP-10 USB Multiplexer | `${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/UQFN-10_1.4x1.8mm_P0.4mm.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/UQFN-10_1.4x1.8mm_P0.4mm.step` |
| **X1** | 3225 24MHz Crystal | `${KICAD10_3DMODEL_DIR}/Crystal.3dshapes/Crystal_SMD_3225-4Pin_3.2x2.5mm.step` | STEP | Resolved | `${KICAD10_3DMODEL_DIR}/Crystal.3dshapes/Crystal_SMD_3225-4Pin_3.2x2.5mm.step` |

---

### 2.2 Deep Investigation of J2 (Molex USB-A Vertical)
- **Assigned Model:** `${KIPRJMOD}/3dmodels/USB_A_Molex_105057-0001_Vertical.wrl`
- **Failure 1 (STEP Export Rejection):** `kicad-cli pcb export step` halts or discards the model with:
  `Cannot use VRML models when exporting to non-mesh formats.`
  VRML (`.wrl`) meshes cannot be translated into B-Rep STEP boundary representations.
- **Failure 2 (Coordinate Scaling Mismatch):** The WRL file coordinates are exported in inches (Z max = 5.708 inches = 145 mm; X = -1.28 to +4.03 inches = 135 mm). Configured with `(scale (xyz 1 1 1))`, it renders distorted or out of scale.
- **Disk File Audit:** The directory `3dmodels/` already contains the full STEP model:
  `3dmodels/USB_A_Molex_105057-0001_Vertical.step` (315,968 bytes).
  - Units: Millimetres (`SI_UNIT(.MILLI.,.METRE.)`)
  - Bounding Box: `X: -3.25 to 10.24 mm`, `Y: -0.96 to 4.96 mm`, `Z: -3.00 to 14.50 mm`.
  - Alignment: Pins align with pad holes `(drill 0.9 mm)` at `(0, 0)`, `(2.5, 0)`, `(4.5, 0)`, `(7.0, 0)` with zero offset `(offset (xyz 0 0 0))` and zero rotation `(rotate (xyz 0 0 0))`.
- **Exact Remediation:** Update `J2` in `CM5-AI-Cam-CopperPilot.kicad_pcb` and `CM5.pretty/MOLEX_USB_67298-4090.kicad_mod`:
  ```lisp
  (model "${KIPRJMOD}/3dmodels/USB_A_Molex_105057-0001_Vertical.step"
      (offset (xyz 0 0 0))
      (scale (xyz 1 1 1))
      (rotate (xyz 0 0 0))
  )
  ```

---

### 2.3 Deep Investigation of Type_C1 (GCT USB-C 16-Pin)
- **Assigned Model:** `${KICAD9_3DMODEL_DIR}/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step`
- **Failure Root Cause:** The board references the KiCad 9 system environment variable `${KICAD9_3DMODEL_DIR}`. On KiCad 10 workstations, only `${KICAD10_3DMODEL_DIR}` is defined by default. The variable expands to an empty string, rendering the footprint model completely absent in 3D viewers and exports.
- **Disk File Audit:** The project already bundles the vendor STEP model inside the project repository:
  `CM5.3dshapes/USB4105-GF-A.step` (2,172,361 bytes).
  *Note on Rotation:* The vendor STEP model has its native CAD coordinates oriented on the Z-plane. In the sibling footprint `CM5.pretty/GCT_USB4105-GF-A.kicad_mod`, it is assigned with `(rotate (xyz -90 0 0))`.
- **Exact Remediation Options:**
  - **Option A (Self-Contained Project Model - Recommended):**
    ```lisp
    (model "${KIPRJMOD}/CM5.3dshapes/USB4105-GF-A.step"
        (offset (xyz 0 0 0))
        (scale (xyz 1 1 1))
        (rotate (xyz -90 0 0))
    )
    ```
  - **Option B (KiCad 10 System Library):**
    ```lisp
    (model "${KICAD10_3DMODEL_DIR}/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step"
        (offset (xyz 0 0 0))
        (scale (xyz 1 1 1))
        (rotate (xyz 0 0 0))
    )
    ```

---

### 2.4 Path Syntax Authority: `${KIPRJMOD}` vs Relative (`./`) in KiCad 10
KiCad 10 resolves paths using project environment variables.
- **Relative paths (`./3dmodels/...`, `./CM5.3dshapes/...`):** KiCad resolves `./` relative to the *Current Working Directory (CWD)* of the host OS process, NOT the project folder. When a user launches KiCad from the desktop or runs CLI tools from outside the repository root, all `./` paths immediately break and fail to render.
- **`${KIPRJMOD}` paths:** KiCad internally binds `${KIPRJMOD}` to the directory containing the project file (`.kicad_pro` / `.kicad_pcb`). It guarantees 100% deterministic, portable resolution across all operating systems, command line tools, and external scripts.
- **Remediation for 5 Footprints with `./` Syntax:**
  - `J1`: Change `./3dmodels/Camera_IMX219-D160.step` -> `${KIPRJMOD}/3dmodels/Camera_IMX219-D160.step`
  - `HDMI1`: Change `./CM5.3dshapes/JTHDA-19F08.STEP` -> `${KIPRJMOD}/CM5.3dshapes/JTHDA-19F08.STEP`
  - `TF1`: Change `./CM5.3dshapes/5033981892.stp` -> `${KIPRJMOD}/CM5.3dshapes/5033981892.stp`
  - `L7`: Change `./CM5.3dshapes/SRP5030CC.stp` -> `${KIPRJMOD}/CM5.3dshapes/SRP5030CC.stp`
  - `Module1`: Change `./CM5.3dshapes/...` -> `${KIPRJMOD}/CM5.3dshapes/...`
