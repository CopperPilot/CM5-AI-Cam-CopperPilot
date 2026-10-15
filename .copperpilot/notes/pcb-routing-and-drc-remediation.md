# PCB Routing Discontinuities, Plane Voids, and DRC Remediation Report

**Target Board:** `CM5-AI-Cam-CopperPilot.kicad_pcb`  
**Toolchain:** KiCad 10.0.3  
**DRC Audit Source:** `.copperpilot/tmp/current_drc.json` & `CM5-AI-Cam-CopperPilot-drc.rpt`  
**Scope:** 13 Unconnected Net Items, 571 DRC Warnings, 4 Split Copper Planes, 6 Dangling Vias, 2 Dangling Tracks  

---

## 1. Inventory & Root-Cause Diagnosis of 13 Unconnected Items

| Item # | Net Name | Endpoint 1 (Coords / Layer / Object) | Endpoint 2 (Coords / Layer / Object) | Defect Mechanism & Root Cause | Specific Routing Strategy |
|---|---|---|---|---|---|
| **1** | `/PWR_3V3` | `(37.3625, 42.5500)` mm<br>B.Cu, Pad 1 of U2 (RT9193-18GB) | `(39.0000, 47.9500)` mm<br>F.Cu, Pad 1 of C26 | **Plane Islanding (In3.Cu Poly 3):** U2.1 (1.8V LDO VIN) drops to In3.Cu Poly 3 `[36.11-48.00, 40.11-55.52]`. Signal tracks (`/SD_CLK`, `/SD_DAT2`, `/SD_VDD_Override`, `/EEPROM_WP`) cut across In3.Cu, severing Poly 3 from main plane Poly 1 where C26 resides. | Route a 0.50 mm trace on B.Cu from U2.1 `(37.3625, 42.5500)` north to Via `(37.6160, 48.4949)` / C26.1, tying Island 3 to the main 3.3V plane. |
| **2** | `/PWR_3V3` | `(53.5000, 47.9800)` mm<br>B.Cu, Track at C5.1 | `(54.6375, 43.2895)` mm<br>F.Cu-B.Cu, Via on Poly 1 | **Plane Islanding (In3.Cu Poly 5):** C5.1 (U7 bypass) and U3.1 (1.2V LDO VIN) drop through Via `(53.7766, 48.7125)` into In3.Cu Poly 5 `[43.75-54.00, 35.32-50.00]`. High-speed traces (`/CSI_D1_N`, `/CSI_CLK_P`, `/SD_DAT2`) sever Poly 5 from main plane Poly 1. | Route a 0.50 mm trace on B.Cu from C5.1 `(53.5000, 47.9800)` to Via `(54.6375, 43.2895)`, reconnecting U3 and C5 to the primary 3.3V rail. |
| **3** | `/PWR_3V3` | `(53.5000, 47.9800)` mm<br>B.Cu, Track at C5.1 | `(48.5000, 47.9800)` mm<br>B.Cu, Pad 1 of C12 | **Mutual Islanding (In3.Cu Poly 4 vs Poly 5):** C12.1 drops via `(48.5000, 48.7413)` into In3.Cu Poly 4 `[47.65-49.87, 48.53-50.00]`. Poly 4 is mutually isolated from Poly 5 and Poly 1 by dense signal via corridors. | Route a 0.50 mm trace on B.Cu connecting C12.1 `(48.5000, 47.9800)` to C5.1 `(53.5000, 47.9800)` and onward to Via `(54.6375, 43.2895)`. |
| **4** | `GND` | `(47.5000, 61.0056)` mm<br>B.Cu, Track at Pin 42 | `(45.5299, 61.0922)` mm<br>F.Cu-B.Cu, Via [GND] | **DF40 Mezzanine Ground Antipad Moat:** Connector escape vias at X=47.5 and X=45.5 land on isolated ground pockets on In1.Cu (Poly 3 & 2) and In4.Cu (Poly 3 & 5). High via density creates overlapping 1.0 mm antipads, severing copper. | Bridge ground pins on B.Cu with a 0.40 mm ground tie-track from `(45.5299, 61.0922)` to `(47.5000, 61.0056)`. |
| **5** | `GND` | `(53.1000, 60.3400)` mm<br>B.Cu, Pad 60 of Module1 | `(54.3000, 60.3400)` mm<br>B.Cu, Track at Pin 64 | **DF40 Connector Ground Starvation:** Pin 60 drops through Via `(53.3125, 58.9823)` to isolated Poly 4 (In1.Cu) / Poly 8 (In4.Cu). Pin 64 connects via Via `(55.0649, 61.2890)` to main ground Poly 1. Pin 60 has zero return path to main ground. | Route a 0.40 mm ground tie-track on B.Cu connecting Pad 60 `(53.10, 60.34)` eastward to Pin 64 track `(54.30, 60.34)` and Via `(55.0649, 61.2890)`. |
| **6** | `GND` | `(53.1000, 60.3400)` mm<br>B.Cu, Pad 60 of Module1 | `(51.5000, 60.3400)` mm<br>B.Cu, Pad 52 of Module1 | **Mutual Ground Isolation:** Pin 60 and Pin 52 (via `(51.3039, 59.1865)` to In1.Cu Poly 5 / In4.Cu Poly 7) sit on isolated copper fragments. Neither connects to system ground, nor to each other. | Extend the continuous B.Cu ground bus across pins 52, 54, 56, 58, 60, tying all pins together into the main ground via at `(55.0649, 61.2890)`. |
| **7** | `/CM5_5V` | `(56.9878, 63.4800)` mm<br>F.Cu, Track at C23.1 | `(33.4000, 58.8200)` mm<br>F.Cu, Pad A9 of Type_C1 | **12.75 mm Plane Void on In3.Cu:** In3.Cu 5V zone is partitioned into Poly 1 `[21.65-42.68]` (Type-C) and Poly 2 `[55.43-76.35]` (CM5 & regulators). 47 escape vias between X=42.7 and 55.4 create a continuous 1.0 mm antipad wall. USB-C 5V cannot reach the board. | Route a heavy copper track (width >= 1.2 mm) or polygon pour on F.Cu along the lower board edge from Type_C1 `(33.40, 58.82)` to C23.1 / C22.1 `(56.9878, 63.4800)`. |
| **8** | `/CSI_D0_N` | `(56.5125, 33.3250)` mm<br>F.Cu, Pad 3 of L1 (ACM1210) | `(57.3625, 43.0000)` mm<br>F.Cu, Pad 23 of J1 (FH12-30S) | **Omitted High-Speed Differential Route:** Net has 0 segments and 0 vias. Partner net `/CSI_D0_P` is routed (L1.2 to J1.24 via In1.Cu), but `/CSI_D0_N` was omitted. MIPI CSI data reception is dead. | Route `/CSI_D0_N` as a differential pair coupled to `/CSI_D0_P`: F.Cu pad L1.3 -> Via `(56.0, 34.5)` -> In1.Cu (0.125 mm trace, 0.15 mm gap) -> Via `(56.8, 41.5)` -> F.Cu pad J1.23. Match length within 0.1 mm. |
| **9** | `/MP1658_SW` | `(67.2293, 36.7868)` mm<br>F.Cu, Track at SW node | `(66.0000, 37.9600)` mm<br>F.Cu, Pad 1 of R16 | **Missing Tap to Passing Net:** R16 (bootstrap damper) Pad 1 is placed 1.0 mm from the heavy SW trace connecting U5.2, C24.1, and L7.1, but was never connected. Bootstrap capacitor cannot charge. | Route a 0.35 mm trace on F.Cu from R16.1 `(66.00, 37.96)` to tap directly into the passing SW trace at `(66.60, 36.50)`. |
| **10** | `/MP1658_BST` | `(66.6027, 37.3573)` mm<br>F.Cu, Dangling Track end | `(67.0105, 41.4500)` mm<br>F.Cu, Dangling Track end | **3.1 mm Routing Gap:** Route from C24.2 transitions from In3.Cu through Via `(66.6027, 36.9239)` to F.Cu and dead-ends at `(66.6027, 37.3573)`. Route from U5.4 stops at `(66.0, 40.4395)`. High-side driver unpowered. | Bridge the 3.1 mm open gap on F.Cu with a 0.30 mm trace running from `(66.6027, 37.3573)` to `(66.0000, 40.4395)` and `(67.0105, 41.4500)`. |
| **11** | `/1V2` | `(49.6375, 42.5500)` mm<br>B.Cu, Track at U3.5 / C15.1 | `(60.0625, 41.4000)` mm<br>F.Cu, Pad 4 of J1 | **Omitted Camera Core Supply Route:** U3 output feeds local capacitors C15 (B.Cu) and C7 (F.Cu) via Via `(48.5883, 35.0987)`, but the feed across to camera socket J1 Pad 4 was omitted. Camera core is completely unpowered. | Route a 0.40 mm power trace on F.Cu from C7.1 / Via `(48.5883, 35.0987)` eastward along Y=41.4 mm to terminate at J1 Pad 4 `(60.0625, 41.4000)`. |
| **12** | `/SDA_1V8` | `(32.8500, 43.9250)` mm<br>B.Cu, Pad 2 of Q2 | `(32.5000, 45.4900)` mm<br>B.Cu, Pad 2 of R8 | **Omitted Pull-up Resistor Connection:** Camera I2C bus routes from J1.30 to level shifter Q2.2 on B.Cu. Pull-up resistor R8 is placed adjacent at `(32.50, 45.49)`, but Pad 2 was never wired. Bus floats high-Z. | Route a 0.25 mm trace on B.Cu directly from R8 Pad 2 `(32.50, 45.49)` to Q2 Pad 2 `(32.85, 43.925)` (trace length 1.6 mm). |
| **13** | `/CM5_3V3` | `(27.0229, 35.0684)` mm<br>F.Cu-B.Cu, Via [CM5_3V3] | `(29.5000, 33.4255)` mm<br>B.Cu, Track at U6.9 / C28.1 | **Severed Pull-up Supply Branch:** Via `(27.0229, 35.0684)` connects on B.Cu to R28.2 (`USB_SEL` pull-up), but dead-ends on F.Cu without connecting to the `CM5_3V3` trunk at Via `(30.2606, 33.4497)` / U6.9. | Route a 0.25 mm trace on F.Cu from Via `(27.0229, 35.0684)` to Via `(30.2606, 33.4497)` or U6 Pad 9. |

---

## 2. Power Plane & Antipad Analysis

### 2.1 Stackup & Zone Definition
- **In1.Cu (Layer 4):** Zone `GND` (8 filled polygons).
- **In2.Cu (Layer 6):** Signal routing layer (high-speed differential pairs).
- **In3.Cu (Layer 8):** Split Power Plane:
  - Zone `/PWR_3V3` (5 filled polygons).
  - Zone `/CM5_5V` (2 filled polygons).
- **In4.Cu (Layer 10):** Zone `GND` (18 filled polygons).

### 2.2 Antipad Geometry and Overlap Mechanism
- **Standard Via Dimensions:** Pad diameter $D_{pad} = 0.50\text{ mm}$, Drill diameter $D_{drill} = 0.25\text{ mm}$.
- **Zone Clearance Constraint:** Clearance $C = 0.25\text{ mm}$ (`connect_pads (clearance 0.25)`).
- **Antipad Diameter:**
  $$D_{antipad} = D_{pad} + 2 \times C = 0.50 + 2(0.25) = 1.00\text{ mm}$$
- **Antipad Overlap Condition:**
  When center-to-center pitch between two adjacent vias is $P < D_{antipad} = 1.00\text{ mm}$, the antipads overlap by:
  $$\Delta_{overlap} = 1.00\text{ mm} - P$$

### 2.3 The 12.75 mm `/CM5_5V` Plane Void
In Zone `/CM5_5V` on In3.Cu, the copper pour is divided into:
- **Poly 1 (West):** `X: [21.65, 42.68] mm, Y: [58.50, 64.85] mm` (Area span: 21.03 x 6.35 mm, 486 vertices). Connected to Type_C1 VBUS.
- **Poly 2 (East):** `X: [55.43, 76.35] mm, Y: [25.15, 64.85] mm` (Area span: 20.92 x 39.70 mm, 2874 vertices). Feeds CM5 mezzanine power pins and buck regulator U5.
- **The Severing Corridor:** The region `X: [42.68, 55.43] mm, Y: [58.00, 65.00] mm` has a total width of **12.75 mm**.
- **Physical Blocker:** Exactly **47 connector escape vias** are placed along this corridor. 25 adjacent via pairs have center-to-center pitch below 1.00 mm (down to 0.474 mm pitch, yielding overlaps up to 0.376 mm). The continuous overlap creates an impassable copper trench, completely isolating Poly 1 from Poly 2. Zone refill cannot heal this void because the physical clearance rules prohibit copper generation between antipads.

### 2.4 `/PWR_3V3` Plane Trenching & Islanding
On In3.Cu, Zone `/PWR_3V3` is fragmented into 5 polygons:
- **Poly 1:** `X: [21.65, 67.00] mm, Y: [25.15, 58.00] mm` (Main solid plane, 12,152 vertices).
- **Poly 2:** `X: [44.71, 48.00] mm, Y: [55.44, 58.00] mm` (Floating fragment, 173 vertices).
- **Poly 3:** `X: [36.11, 48.00] mm, Y: [40.11, 55.52] mm` (Isolates U2.1 & C25.1, 562 vertices).
- **Poly 4:** `X: [47.65, 49.87] mm, Y: [48.53, 50.00] mm` (Isolates C12.1, 25 vertices).
- **Poly 5:** `X: [43.75, 54.00] mm, Y: [35.32, 50.00] mm` (Isolates C5.1 & U3.1, 316 vertices).
- **Milling Mechanism:** 137 signal trace segments belonging to 11 non-power nets (`/SD_DAT2`, `/SD_CLK`, `/SD_VDD_Override`, `/BT_EN`, `/EEPROM_WP`, `/LED_G`, `/CSI_D1_N`, `/CSI_CLK_P`, `/CM5_3V3`, `/GPIO18`, `/GPIO22`) were routed directly on In3.Cu. These traces cut trenches across the power copper. Combined with `(island_removal_mode 0)`, KiCad preserves the detached copper, leaving IC loads powered only by dead islands.

### 2.5 Ground Return Discontinuities (In1.Cu & In4.Cu)
- In1.Cu contains 8 polygons; In4.Cu contains 18 polygons.
- Under the DF40 connector (Module1), ground pins at X = 45.5, 47.5, 51.5, and 53.1 mm drop through vias into isolated ground islands.
- High-speed return currents flowing on In1.Cu and In4.Cu cannot return directly under their respective signal traces. The return currents are forced around the 12.7 mm via trench, creating extensive loop inductance, radiated emissions, and ground bounce during GPIO/CSI switching.

---

## 3. Categorization & Batch Resolution of 571 DRC Violations

The 571 DRC violations in `current_drc.json` fall into 8 distinct failure modes:

| DRC Warning Key | Count | Root Cause / Physical Mechanism | Affected Components / Locations | Automated Batch Resolution Path |
|---|---:|---|---|---|
| `silk_overlap` | 199 | Silkscreen text and footprint lines placed < 0.15 mm from neighboring silkscreen elements. | Concentrated on dense passives: J1 (12), R36 (10), R35 (10), L3 (9), R20 (8), L7 (8), C27 (8), L1 (8), C24 (7), L2 (7). | Execute batch Python script to push reference designator positions outward along component centerline by 0.35 mm; or configure `.kicad_pro` `silk_clearance` to 0.10 mm (supported by JLCPCB standard silkscreen capability). |
| `silk_over_copper` | 199 | Silkscreen line segments or text encroaching on solder mask openings of component pads (clearance < 0.15 mm). | J1 (13), U5 (12), L2 (12), R35 (11), L3 (11), R36 (8), DSI1 (8), C19 (8), C27 (8), C24 (7), R20 (7). | Run automated silkscreen clipping script to retract F.SilkS and B.SilkS segments that intersect pad solder mask bounding boxes plus 0.15 mm margin. Alternatively, enable Gerber CAM clipping during export. |
| `lib_footprint_issues` | 90 | Footprint library table entry `CM5` specifies a non-portable hardcoded absolute URI (`/Users/adityang/Projects/CM5-AI-Cam-CopperPilot/CM5.pretty`) which fails lookup. | Exactly all 90 placed footprints on the board. | Edit `fp-lib-table` to replace the absolute URI with the portable project-relative path `(uri "${KIPRJMOD}/CM5.pretty")`. This clears all 90 warnings in one transaction. |
| `nonmirrored_text_on_back_layer` | 54 | Footprint text properties on `B.SilkS`, `B.Fab`, or `B.Cu` lack the `(effects (justify mirror))` attribute, causing text to read backwards on bottom side. | Exactly all 54 footprints placed on layer `B.Cu` (R33, L6, R2, R14, R22, R31, R15, C32, FB1, R28, etc.). | Execute batch regex/Python script on `CM5-AI-Cam-CopperPilot.kicad_pcb` to inject `mirror` into the `justify` property of all text elements located on back layers. |
| `silk_edge_clearance` | 18 | Silkscreen outlines located within 0.15 mm of `Edge.Cuts` boundary. | Module1 B.SilkS courtyard (10 violations: X=21.3, 76.3, Y=24.9, 64.9); DSI1 F.SilkS outline (4 violations: Y=25.09, 26.39); HDMI1 F.SilkS outline (4 violations: X=22.0, 37.0). | In footprint `Raspberry-Pi-5-Compute-Module.kicad_mod`, move the 55x40 mm outer bounding box from `B.SilkS` to `B.Fab`. Retract DSI1 and HDMI1 silkscreen edge segments inward by 0.50 mm. |
| `via_dangling` | 6 | Vias placed with no outer-layer connections, or broken stubs. | Vias at `(22.2, 52.0)`, `(23.4, 26.2)`, `(32.0, 64.2)`, `(74.0, 25.8)`, `(75.8, 42.0)`, `(27.0229, 35.0684)`. | Delete 4 orphan vias; finish 2 functional vias (connect HDMI shield via and R28.2 pull-up branch). Detailed in Section 4. |
| `text_thickness` | 3 | Text stroke width below DRC constraint threshold of 0.15 mm. | PCB text `'CM5 AI Camera Carrier Board'` on F.Silkscreen `(37.5, 62.5)` (TrueType font weight); J1 Reference field `(48.2125, 35.8)` (0.12 mm); J1 footprint text `(43.7125, 38.5)` (0.12 mm). | Update J1 footprint text stroke width from 0.12 mm to 0.15 mm; update board title text font thickness to 0.15 mm (or switch to standard KiCad stroke font). |
| `track_dangling` | 2 | Open-ended track segments terminating in free space. | Tracks on net `/MP1658_BST` at `(66.6027, 37.3573)` (length 0.43 mm) and `(67.0105, 41.4500)` (length 1.43 mm). | Bridge the 3.1 mm open gap on F.Cu between the two track stubs to complete the bootstrap capacitor circuit. |

---

## 4. Dangling Vias & Stub Traces Action Plan

### 4.1 Dangling Vias (6 Items)
1. **Via `[/PWR_3V3]` at `(22.2000, 52.0000)` mm `[F.Cu - B.Cu]` (Size 0.5 mm, Drill 0.25 mm)**
   - *Status:* **Orphan Via / Antenna Stub — DELETE.**
   - *Analysis:* Located on far left edge inside Zone 2 boundary. Zero connected tracks on F.Cu or B.Cu; nearest 3.3V load is > 8 mm away. Serves no electrical function.
2. **Via `[GND]` at `(23.4000, 26.2000)` mm `[F.Cu - B.Cu]` (Size 0.5 mm, Drill 0.25 mm)**
   - *Status:* **Incomplete Shield Grounding — FINISH.**
   - *Analysis:* Located 0.82 mm from HDMI connector shield tab `HDMI1.SH` `(22.75, 27.02)`. Connects to internal planes In1.Cu/In4.Cu. Route a 0.50 mm trace on F.Cu from `HDMI1.SH` to this via to provide low-impedance connector shell chassis grounding.
3. **Via `[/CM5_5V]` at `(32.0000, 64.2000)` mm `[F.Cu - B.Cu]` (Size 0.5 mm, Drill 0.25 mm)**
   - *Status:* **Orphan Via / Antenna Stub — DELETE.**
   - *Analysis:* Located along bottom edge below Type_C1. Drops into 5V Poly 1, but has no trace connections on outer layers. Leftover from prior routing pass.
4. **Via `[/CM5_5V]` at `(74.0000, 25.8000)` mm `[F.Cu - B.Cu]` (Size 0.5 mm, Drill 0.25 mm)**
   - *Status:* **Orphan Via / Antenna Stub — DELETE.**
   - *Analysis:* Located at top right corner inside Poly 2. No surface traces or 5V components nearby.
5. **Via `[/CM5_5V]` at `(75.8000, 42.0000)` mm `[F.Cu - B.Cu]` (Size 0.5 mm, Drill 0.25 mm)**
   - *Status:* **Orphan Via / Antenna Stub — DELETE.**
   - *Analysis:* Located on far right edge near header H5. Header H5 consumes only 3.3V and 1.8V. No outer layer connection.
6. **Via `[/CM5_3V3]` at `(27.0229, 35.0684)` mm `[F.Cu - B.Cu]` (Size 0.5 mm, Drill 0.25 mm)**
   - *Status:* **Broken Functional Trunk — FINISH.**
   - *Analysis:* Directly tied on B.Cu to pull-up resistor R28.2 (`USB_SEL`), but dead-ends on F.Cu. Causes Unconnected Item 13. Route a 0.25 mm trace on F.Cu to connect this via to `CM5_3V3` trunk at Via `(30.2606, 33.4497)` / U6.9.

### 4.2 Dangling Tracks (2 Items)
1. **Track `[/MP1658_BST]` at `(66.6027, 37.3573)` mm `[F.Cu, length 0.4334 mm, width 0.25 mm]`**
   - *Analysis:* Originates at Via `(66.6027, 36.9239)` coming from bootstrap cap C24.2 on In3.Cu; terminates abruptly in open air. Forms western half of Unconnected Item 10.
2. **Track `[/MP1658_BST]` at `(67.0105, 41.4500)` mm `[F.Cu, length 1.4291 mm, width 0.25 mm]`**
   - *Analysis:* Originates at regulator pin U5.4 and routes northwest to `(66.0, 40.4395)`. Forms eastern half of Unconnected Item 10.
   - *Remediation:* Connect `(66.6027, 37.3573)` to `(66.0000, 40.4395)` with a 0.30 mm trace on F.Cu, bridging the 3.1 mm gap.

---

## 5. Complete Routing Remediation Plan

### Phase 1: Environment & Library Setup
1. Edit `fp-lib-table`: replace `(uri "/Users/adityang/Projects/CM5-AI-Cam-CopperPilot/CM5.pretty")` with `(uri "${KIPRJMOD}/CM5.pretty")`.
2. Clear 90 `lib_footprint_issues`.

### Phase 2: Silkscreen & Text Remediation
1. **Mirror Bottom Layer Text:** In `CM5-AI-Cam-CopperPilot.kicad_pcb`, identify all 54 footprints on layer `B.Cu`. For every `fp_text` and `property` on layers `B.SilkS`, `B.Fab`, and `B.Cu`, ensure `(justify mirror)` is present in `(effects ...)`. Clears 54 `nonmirrored_text_on_back_layer`.
2. **Module Courtyard Silkscreen Fix:** In `CM5.pretty/Raspberry-Pi-5-Compute-Module.kicad_mod`, reassign the 55x40 mm outer rectangle and corner arcs from layer `B.SilkS` to `B.Fab`. Clears 10 `silk_edge_clearance` warnings.
3. **Connector Silkscreen Retraction:** In `CM5.pretty/Hirose_FH12-30S-0.5SH_1x30-1MP_P0.50mm_Horizontal.kicad_mod` (DSI1) and `CM5.pretty/HDMI_Mini-C_Molex_47151-0001.kicad_mod` (HDMI1), pull back silkscreen line ends by 0.50 mm from the board boundary. Clears remaining 8 `silk_edge_clearance` warnings.
4. **Text Thickness Normalization:** Update J1 reference and pin indicator text stroke width to 0.15 mm. Set board title text stroke thickness to 0.15 mm. Clears 3 `text_thickness` warnings.
5. **Silkscreen Overlap & Over-Copper Pushback:** Apply automated designator pushback script to shift colliding reference designators by 0.35 mm away from pad solder mask openings. Clears 199 `silk_overlap` and 199 `silk_over_copper` warnings.

### Phase 3: Layout Stub & Orphan Via Pruning
1. Remove 4 orphan vias:
   - Via at `(22.2000, 52.0000)` mm `[/PWR_3V3]`
   - Via at `(32.0000, 64.2000)` mm `[/CM5_5V]`
   - Via at `(74.0000, 25.8000)` mm `[/CM5_5V]`
   - Via at `(75.8000, 42.0000)` mm `[/CM5_5V]`

### Phase 4: Power & Ground Discontinuity Routing
1. **`/CM5_5V` High-Current Bridge (Fixes Item 7):**
   - On F.Cu, draw a 1.50 mm wide power trace from Type_C1 VBUS pads `(33.40, 58.82)` running eastward along Y=63.5 mm to C23.1 `(56.9878, 63.4800)` and CM5 mezzanine pins.
   - Add copper fill polygon on F.Cu/B.Cu spanning the corridor to maximize current delivery (> 3A capability).
2. **`/PWR_3V3` Island Interconnects (Fixes Items 1, 2, 3):**
   - Route 0.50 mm trace on B.Cu from U2.1 `(37.3625, 42.5500)` to Via `(37.6160, 48.4949)` / C26.1 (reconnecting Island 3 to main plane).
   - Route 0.50 mm trace on B.Cu from C5.1 `(53.5000, 47.9800)` to Via `(54.6375, 43.2895)` (reconnecting Island 5 to main plane).
   - Route 0.50 mm trace on B.Cu from C12.1 `(48.5000, 47.9800)` to C5.1 `(53.5000, 47.9800)` (reconnecting Island 4).
3. **`GND` DF40 Mezzanine Ground Bus (Fixes Items 4, 5, 6):**
   - On B.Cu, route a continuous 0.40 mm ground tie-track linking ground escape pins:
     `(45.5299, 61.0922)` -> `(47.5000, 61.0056)` -> `(51.5000, 60.3400)` -> `(53.1000, 60.3400)` -> `(54.3000, 60.3400)` -> Via `(55.0649, 61.2890)`.
   - Add 2 ground stitching vias `(46.5, 59.8)` and `(52.2, 59.5)` to tie outer ground traces into internal solid planes In1.Cu/In4.Cu.
4. **HDMI Shield Grounding (Fixes Dangling Via 2):**
   - Route a 0.50 mm trace on F.Cu from `HDMI1.SH` `(22.75, 27.02)` to Via `(23.4000, 26.2000)`.

### Phase 5: Signal & Switching Loop Completion
1. **`/CSI_D0_N` Differential Route (Fixes Item 8):**
   - Route on F.Cu from L1.3 `(56.5125, 33.3250)` to Via at `(56.0, 34.5)`.
   - Transition to In1.Cu (0.125 mm trace width, 0.15 mm edge-to-edge spacing to `/CSI_D0_P`).
   - Route parallel to `/CSI_D0_P` south to Via at `(56.8, 41.5)`.
   - Transition to F.Cu and terminate at J1 Pad 23 `(57.3625, 43.0000)`.
   - Total routed length: match `/CSI_D0_P` length (approx. 11.2 mm) within 0.1 mm tolerance.
2. **`/MP1658_SW` Resistor Tap (Fixes Item 9):**
   - Route 0.35 mm trace on F.Cu from R16 Pad 1 `(66.0000, 37.9600)` to tap into the SW node trace at `(66.60, 36.50)`.
3. **`/MP1658_BST` Loop Closure (Fixes Item 10 & Dangling Tracks 1, 2):**
   - Bridge the 3.1 mm open gap on F.Cu with a 0.30 mm trace connecting `(66.6027, 37.3573)` to `(66.0000, 40.4395)` and `(67.0105, 41.4500)`.
4. **`/1V2` Camera Core Feed (Fixes Item 11):**
   - Route 0.40 mm trace on F.Cu from C7.1 / Via `(48.5883, 35.0987)` eastward along Y=41.4 mm to J1 Pad 4 `(60.0625, 41.4000)`.
5. **`/SDA_1V8` Pull-up Connection (Fixes Item 12):**
   - Route 0.25 mm trace on B.Cu connecting R8 Pad 2 `(32.5000, 45.4900)` to Q2 Pad 2 `(32.8500, 43.9250)`.
6. **`/CM5_3V3` Branch Connection (Fixes Item 13 & Dangling Via 6):**
   - Route 0.25 mm trace on F.Cu from Via `(27.0229, 35.0684)` to Via `(30.2606, 33.4497)` / U6 Pad 9.

### Phase 6: Zone Refill & Signoff Verification
1. Execute `kicad-cli pcb drc --refill-zones` against `CM5-AI-Cam-CopperPilot.kicad_pcb`.
2. Confirm 0 unconnected items, 0 dangling vias/tracks, and 0 DRC violations.
3. Regenerate Gerber and drill files for JLCPCB production.
