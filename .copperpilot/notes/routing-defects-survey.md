# Routing Defects and DRC Disconnection Survey

**Target Board:** `CM5-AI-Cam-CopperPilot.kicad_pcb`  
**Toolchain:** KiCad 10.0.3  
**DRC Reference Report:** `CM5-AI-Cam-CopperPilot-drc.rpt`  
**Summary of Findings:** 13 unconnected items, 2 dangling tracks, 6 dangling vias. Zone refill evaluated and confirmed insufficient to resolve any defect without layout intervention.

---

## 1. Inventory & Root-Cause Diagnosis of the 13 Unconnected Items

| Item # | Net Name | Coordinates (Point 1 / Point 2) | Affected Items (Component Pads / Tracks / Vias) | Physical Mechanism / Root Cause |
|---|---|---|---|---|
| 1 | `/PWR_3V3` | Pt1: (37.3625, 42.5500) mm [B.Cu]<br>Pt2: (39.0000, 47.9500) mm [F.Cu] | Track on B.Cu connecting U2.1 & Via (37.3625, 41.7687) vs Pad 1 of C26 on F.Cu | **Isolated Plane Island (Poly 3 on In3.Cu):** U2 (1.8V LDO VIN) and input decoupling capacitor C25 connect to a small copper island on In3.Cu. Signal routing on In3.Cu (`/SD_CLK`, `/SD_DAT2`, `/SD_VDD_Override`, `/EEPROM_WP`) slices across In3.Cu, completely severing this island from the main 3.3V plane (Poly 1) where C26 resides. |
| 2 | `/PWR_3V3` | Pt1: (53.5000, 47.9800) mm [B.Cu]<br>Pt2: (54.6375, 43.2895) mm [F.Cu-B.Cu] | Track on B.Cu at C5.1 vs Via at (54.6375, 43.2895) on In3.Cu Poly 1 | **Isolated Plane Island (Poly 5 on In3.Cu):** C5.1 (input bypass for U7) and U3.1 (VIN for 1.2V LDO) connect through Via (53.7766, 48.7125) to In3.Cu island Poly 5. Dense signal tracks (`/CSI_D1_N`, `/CSI_CLK_P`, `/SD_DAT2`) cut through In3.Cu, isolating Poly 5 from main plane Poly 1 containing Via (54.6375, 43.2895). |
| 3 | `/PWR_3V3` | Pt1: (53.5000, 47.9800) mm [B.Cu]<br>Pt2: (48.5000, 47.9800) mm [B.Cu] | Track at C5.1 [B.Cu] vs Track at C12.1 [B.Cu] | **Isolated Plane Island (Poly 5 vs Poly 4 on In3.Cu):** C12.1 drops through Via (48.5000, 48.7413) to In3.Cu island Poly 4. C5.1 drops through Via (53.7766, 48.7125) to In3.Cu island Poly 5. Both islands are separated by an antipad moat formed by through-hole/via corridors and signal lines. |
| 4 | `GND` | Pt1: (47.6895, 61.1951) mm [B.Cu]<br>Pt2: (45.5299, 61.0922) mm [F.Cu-B.Cu] | Track on B.Cu at Via (47.6895, 61.1951) vs Via (45.5299, 61.0922) | **DF40 Connector Via Fence Severing Ground Planes:** CM5 connector Module1 ground escape pins at X=47.5 mm and X=45.5 mm have vias landing on isolated ground islands (In1.Cu Polys 3 & 2; In4.Cu Polys 3 & 5). High via density from 0.4mm pitch signal escapes produces overlapping antipads (1.0mm diameter) that sever internal ground copper. |
| 5 | `GND` | Pt1: (53.1000, 60.3400) mm [B.Cu]<br>Pt2: (54.3000, 60.3400) mm [B.Cu] | Track on B.Cu at X=53.1 mm vs Track on B.Cu at X=54.3 mm | **DF40 Connector Ground Island vs Main Plane:** Pin at X=53.1 mm connects via Via (53.3125, 58.9823) to isolated island Poly 4 on In1.Cu / Poly 8 on In4.Cu. Pin at X=54.3 mm connects via Via (55.0649, 61.2890) to the main solid ground plane (Poly 1). The 53.1 mm pin is starved of ground return. |
| 6 | `GND` | Pt1: (53.1000, 60.3400) mm [B.Cu]<br>Pt2: (51.5000, 60.3400) mm [B.Cu] | Track on B.Cu at X=53.1 mm vs Track on B.Cu at X=51.5 mm | **Mutual Ground Islanding:** Pin at X=53.1 mm (In1.Cu Poly 4, In4.Cu Poly 8) and pin at X=51.5 mm (In1.Cu Poly 5, In4.Cu Poly 7 via 51.3039, 59.1865) land on separate isolated pockets. Neither connects to main ground, nor to each other. |
| 7 | `/CM5_5V` | Pt1: (56.9878, 63.4800) mm [F.Cu]<br>Pt2: (33.4000, 58.8200) mm [F.Cu] | Track at C23.1 [F.Cu] near CM5 input vs Pad A9 of Type_C1 [F.Cu] | **Split Power Plane Discontinuity on In3.Cu:** Zone 3 (/CM5_5V on In3.Cu) is partitioned into two disjoint filled copper polygons: Poly 1 on the left (X: 21.65 to 42.68 mm, receiving Type-C 5V) and Poly 2 on the right (X: 55.43 to 76.35 mm, supplying CM5 Module1 and regulators). The 12.7 mm corridor between X=42.7 and 55.4 is blocked by 47 overlapping via antipads from connector escapes. Zero copper connects USB 5V to the board. |
| 8 | `/CSI_D0_N` | Pt1: (56.5125, 33.3250) mm [F.Cu]<br>Pt2: (57.3625, 43.0000) mm [F.Cu] | Pad 3 of common-mode choke L1 vs Pad 23 of camera FPC connector J1 | **Completely Unrouted Net:** Net has exactly 0 segments and 0 vias. The positive partner `/CSI_D0_P` was routed (L1.2 to J1.24 via In1.Cu), but `/CSI_D0_N` was omitted entirely during layout. |
| 9 | `/MP1658_SW` | Pt1: (67.2293, 36.7868) mm [F.Cu]<br>Pt2: (66.0000, 37.9600) mm [F.Cu] | Passing SW power track on F.Cu vs Pad 1 of R16 on F.Cu | **Missing Tap to Passing Net:** R16 is the bootstrap damping resistor. Pad 1 (/MP1658_SW) at (66.0, 37.96) is located ~1.0 mm away from the main SW trace connecting U5.2, C24.1, and L7.1, but no segment connects Pad 1 to the passing trace. |
| 10 | `/MP1658_BST` | Pt1: (66.6027, 37.3573) mm [F.Cu]<br>Pt2: (67.0105, 41.4500) mm [F.Cu] | Incomplete track from Via (66.6027, 36.9239) vs Incomplete track from U5.4 | **Broken Route / Unrouted Gap:** The route from bootstrap capacitor C24.2 transitions through In3.Cu and via (66.6027, 36.9239) to F.Cu, ending at a dead stub at (66.6027, 37.3573). The route from U5.4 runs to (66.0, 40.4395). A 3.1 mm unrouted gap separates the two ends. |
| 11 | `/1V2` | Pt1: (49.6375, 41.1175) mm [B.Cu]<br>Pt2: (60.0625, 41.4000) mm [F.Cu] | Track on B.Cu connecting U3.5, C15.1, C7.1 vs Pad 4 of camera connector J1 | **Missing Connector Power Feed:** U3 (1.2V LDO) output is routed to local bypass caps C15 on B.Cu and C7 on F.Cu via Via (48.5883, 35.0987). The branch extending from C7 / the via across to camera connector J1 pad 4 (60.0625, 41.4000) was never routed. Camera core rail is unpowered. |
| 12 | `/SDA_1V8` | Pt1: (32.8500, 43.9250) mm [B.Cu]<br>Pt2: (32.5000, 45.4900) mm [B.Cu] | Pad 2 of level shifter Q2 [B.Cu] vs Pad 2 of pull-up resistor R8 [B.Cu] | **Unconnected Pull-up Pad:** Net `/SDA_1V8` is routed from camera connector J1.30 via In4.Cu to Q2.2 at (32.85, 43.925). Pull-up resistor R8 is placed directly adjacent at (32.50, 45.49) on B.Cu, but Pad 2 was never tied to Q2.2 or the via. |
| 13 | `/CM5_3V3` | Pt1: (27.0229, 35.0684) mm [F.Cu-B.Cu]<br>Pt2: (29.5000, 33.4255) mm [B.Cu] | Via at (27.0229, 35.0684) vs Track on B.Cu connecting U6.9 & C28.1 | **Incomplete Route Branch:** Net `/CM5_3V3` routes from Module1 pins 84/86 via In2.Cu to Via (30.2606, 33.4497), feeding USB switch U6.9 and C28.1. A stub with Via (27.0229, 35.0684) connects to R28.2 (USB_SEL pullup) on B.Cu, but the via dead-ends on F.Cu with no trace back to the rest of `CM5_3V3`. |

---

## 2. Analysis of Dangling Tracks and Dangling Vias

The DRC report flags 6 dangling vias and 2 dangling tracks. Each has been geometrically traced and classified as either an **abandoned stub to delete** or an **incomplete trace to finish**:

### Dangling Vias (6 Items)
1. **Via `[/PWR_3V3]` at (22.2000, 52.0000) mm [F.Cu - B.Cu]**
   - *Status:* **Antenna stub / Orphan via — DELETE.**
   - *Detail:* Located on the far left board edge. While its barrel penetrates In3.Cu (within the boundary of Zone 2), it has zero connected tracks on F.Cu or B.Cu, and no 3.3V loads exist within 8 mm. It was placed as an accidental stitch or leftover via and serves only as an ungrounded antenna stub.
2. **Via `[GND]` at (23.4000, 26.2000) mm [F.Cu - B.Cu]**
   - *Status:* **Incomplete shield connection — FINISH (or delete).**
   - *Detail:* Located 0.8 mm from HDMI connector shield pad `HDMI1.SH` (22.75, 27.02). It penetrates internal ground planes In1.Cu and In4.Cu, but has no trace on F.Cu or B.Cu. Connecting this via to `HDMI1.SH` with a short 0.5 mm surface trace provides direct low-inductance chassis-to-ground grounding. If not connected, it is a dangling stub.
3. **Via `[/CM5_5V]` at (32.0000, 64.2000) mm [F.Cu - B.Cu]**
   - *Status:* **Antenna stub / Orphan via — DELETE.**
   - *Detail:* Located along the bottom edge below Type_C1. Penetrates In3.Cu inside the isolated 5V left polygon, but has no connected traces on F.Cu or B.Cu. Serves no purpose.
4. **Via `[/CM5_5V]` at (74.0000, 25.8000) mm [F.Cu - B.Cu]**
   - *Status:* **Antenna stub / Orphan via — DELETE.**
   - *Detail:* Located at the top right corner of the board. Penetrates In3.Cu inside Poly 2, but has zero track connections on outer layers and no 5V components nearby.
5. **Via `[/CM5_5V]` at (75.8000, 42.0000) mm [F.Cu - B.Cu]**
   - *Status:* **Antenna stub / Orphan via — DELETE.**
   - *Detail:* Located on the right board edge near header H5. Header H5 does not consume 5V (only 3.3V and 1.8V). Zero track connections on outer layers.
6. **Via `[/CM5_3V3]` at (27.0229, 35.0684) mm [F.Cu - B.Cu]**
   - *Status:* **Broken route — FINISH.**
   - *Detail:* Connects on B.Cu to pull-up resistor R28.2 (for `USB_SEL`), but terminates with no connection on F.Cu. This directly causes Unconnected Item 13. A trace must be added on F.Cu (or In2.Cu) to join this via to `CM5_3V3` at Via (30.2606, 33.4497) or U6.9.

### Dangling Tracks (2 Items)
1. **Track `[/MP1658_BST]` at (66.6027, 37.3573) mm [F.Cu, length 0.4334 mm]**
   - *Status:* **Incomplete route — FINISH.**
   - *Detail:* Originates at Via (66.6027, 36.9239) coming from C24.2 on In3.Cu and terminates abruptly in open air. Forms the western half of Unconnected Item 10.
2. **Track `[/MP1658_BST]` at (67.0105, 41.4500) mm [F.Cu, length 1.4291 mm]**
   - *Status:* **Incomplete route — FINISH.**
   - *Detail:* Originates at regulator pin U5.4 and routes toward (66.0, 40.4395), where it stops. Forms the eastern half of Unconnected Item 10.
   - *Fix:* Bridge the 3.1 mm open segment between (66.6027, 37.3573) and (66.0, 40.4395) on F.Cu.

---

## 3. Copper Pours & Zone Fill Assessment

### Stackup Layer Summary & Zone Assignments
- **F.Cu (Layer 0, Outer Signal):** No copper zones.
- **In1.Cu (Layer 4, Internal Plane/Signal):** Zone 1 (`GND`). 8 filled polygons.
- **In2.Cu (Layer 6, Internal High-Speed Signal):** No copper zones.
- **In3.Cu (Layer 8, Internal Power Plane):** Split power plane.
  - Zone 2: `/PWR_3V3` (5 filled polygons).
  - Zone 3: `/CM5_5V` (2 filled polygons).
- **In4.Cu (Layer 10, Internal Ground Plane/Signal):** Zone 4 (`GND`). 18 filled polygons.
- **B.Cu (Layer 2, Outer Signal/Component):** No copper zones.

### Verification of Zone Refill Behavior
Executing `kicad-cli pcb drc --refill-zones` against `CM5-AI-Cam-CopperPilot.kicad_pcb` generates exactly identical results: **571 DRC violations, 13 unconnected items**.
**Conclusion:** Zone refill alone does NOT resolve any of the 13 unconnected items or dangling items.

### Root Causes of Plane Failures
1. **Island Removal Mode = 0 (Keep all islands):** All 4 zones specify `(island_removal_mode 0)`. KiCad preserves every isolated copper fragment, even when completely detached from net connectivity.
2. **Routing Signals across Power Plane (In3.Cu):** 11 different signal nets (`/SD_DAT2`, `/SD_CLK`, `/SD_VDD_Override`, `/BT_EN`, `/EEPROM_WP`, `/LED_G`, `/CSI_D1_N`, `/CSI_CLK_P`, `/CM5_3V3`) were routed as long diagonal traces across In3.Cu. These traces cut deep trenches through the `/PWR_3V3` copper, creating 4 dead islands (Polys 2, 3, 4, 5) that isolate U2.1, C25, C12, U3.1, and C5.
3. **High-Density Via Wall Severing `/CM5_5V` (In3.Cu):** A corridor of 47 connector escape through-vias between X=42.7 mm and X=55.4 mm along Y=[58, 65] creates a continuous overlapping antipad fence. The 5V plane is completely severed into two halves: Type-C input on the left and CM5 / regulator supply on the right.
4. **DF40 Connector Ground Islanding (In1.Cu & In4.Cu):** DF40 ground pins at X=45.5, 47.5, 51.5, and 53.1 mm drop through vias into local isolated ground copper pockets enclosed by dense signal escape routing. Because the escape tracks on B.Cu do not stitch across pins, these ground pins float with respect to system ground.

---

## 4. Specific Routing Action Plan per Net

### Net `/PWR_3V3` (Fixes Items 1, 2, 3)
1. **Bridge Island 3 to Main Plane:** On B.Cu or In3.Cu, route a 0.5 mm trace from Via (37.3625, 41.7687) / U2.1 north toward the solid `/PWR_3V3` copper near C26 / Via (37.6160, 48.4949).
2. **Bridge Island 5 and Island 4 to Main Plane:** On B.Cu, route a 0.5 mm trace connecting C5.1 (53.5, 47.98), C12.1 (48.5, 47.98), and U3.1 (49.6375, 42.55) to the intact 3.3V plane at Via (54.6375, 43.2895).
3. **Delete Orphan Via:** Remove Via at (22.2000, 52.0000) mm.

### Net `GND` (Fixes Items 4, 5, 6 and Dangling Via 2)
1. **CM5 Connector Ground Bus on B.Cu:** Draw a continuous 0.4 mm ground bus trace on B.Cu linking the escape tracks of pins at X = 45.5, 47.5, 49.5, 51.5, 53.1, 54.3, and 55.06 mm. Because Via (55.0649, 61.2890) connects solidly to the main ground plane (Poly 1 on In1.Cu/In4.Cu), this tie-bar brings all connector ground pins directly to system ground.
2. **HDMI Shield Stitching:** Route a 0.4 mm surface trace on F.Cu from `HDMI1.SH` (22.75, 27.02) to Via (23.4000, 26.2000) mm to anchor the shield to internal ground and clear the dangling via.

### Net `/CM5_5V` (Fixes Item 7 and Dangling Vias 3, 4, 5)
1. **Inter-Island 5V Bridge:** Route a dedicated high-current trace (width >= 1.0 mm, or copper polygon) on F.Cu or B.Cu spanning from the Type-C 5V node at (33.4, 58.82) / (32.6, 57.6) across to the CM5 5V bus near C23.1 (56.0, 62.52) / (57.9, 62.57). This bypasses the impassable via wall on In3.Cu and delivers primary 5V power to the board.
2. **Delete Orphan Vias:** Delete the three isolated 5V vias at (32.0, 64.2), (74.0, 25.8), and (75.8, 42.0) mm.

### Net `/CSI_D0_N` (Fixes Item 8)
1. **Differential Pair Routing:** Route `/CSI_D0_N` on F.Cu from choke Pad L1.3 (56.5125, 33.3250) to a new via, through In1.Cu matching `/CSI_D0_P`, and back to F.Cu to terminate at camera connector Pad J1.23 (57.3625, 43.0000). Match trace geometry and length to `/CSI_D0_P` (100 ohm differential impedance).

### Net `/MP1658_SW` (Fixes Item 9)
1. **Connect Bootstrap Resistor Tap:** On F.Cu, route a 0.35 mm trace from R16 Pad 1 (66.0, 37.96) to tap into the passing SW trace at (66.6002, 36.1577) or U5.2 (65.0, 40.5).

### Net `/MP1658_BST` (Fixes Item 10 and Dangling Tracks 1 & 2)
1. **Complete Bootstrap Loop:** Connect the two dangling ends on F.Cu by drawing a 0.3 mm trace from (66.6027, 37.3573) to (66.0, 40.4395), closing the circuit between C24.2 and U5.4.

### Net `/1V2` (Fixes Item 11)
1. **Route Camera Core Supply:** From decoupling cap C7.1 / Via (48.5883, 35.0987) on F.Cu, route a 0.4 mm power trace northeast to camera connector Pad J1.4 at (60.0625, 41.4000).

### Net `/SDA_1V8` (Fixes Item 12)
1. **Tie Pull-up Resistor:** On B.Cu, route a 0.25 mm trace connecting R8 Pad 2 (32.50, 45.49) directly to Q2 Pad 2 at (32.85, 43.925).

### Net `/CM5_3V3` (Fixes Item 13 and Dangling Via 6)
1. **Connect Pull-up Branch:** Route a 0.25 mm trace on F.Cu (or In2.Cu) from Via (27.0229, 35.0684) to Via (30.2606, 33.4497) / U6.9, connecting R28.2 to the 3.3V supply.
