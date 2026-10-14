# JLCPCB 6-Layer Manufacturing Constraints & KiCad Configuration Specification

## 1. Overview and Stackup Architecture

This document defines the comprehensive manufacturing constraints, design rules, controlled impedance geometry, and double-sided SMT assembly specifications for JLCPCB 6-layer PCB fabrication. It maps these physical capabilities directly into KiCad (`.kicad_pro` and `.kicad_dru`).

### 1.1 Standard JLCPCB 6-Layer Stackup Options (1.6 mm Finished Thickness)

JLCPCB offers two primary 6-layer FR4 stackups for 1.6 mm total board thickness:

1. **JLC06161H-3313 (Thin Outer Prepreg ~0.10 mm)**
   * Target: High-density routing, fine-pitch BGA/connectors (e.g., CM5 Hirose DF40), tight differential pairs.
   * L1-to-L2 Prepreg: 3313 (~0.0994 mm, $\varepsilon_r \approx 4.05-4.10$).
   * Core L2-L3: 0.55 mm ($\varepsilon_r \approx 4.5-4.6$).
   * Prepreg L3-L4: 3313 (~0.0994 mm, $\varepsilon_r \approx 4.05-4.10$).
   * Core L4-L5: 0.55 mm ($\varepsilon_r \approx 4.5-4.6$).
   * Prepreg L5-L6: 3313 (~0.0994 mm, $\varepsilon_r \approx 4.05-4.10$).
   * Copper Weight: Outer 1 oz (0.035 mm finished), Inner 0.5 oz (0.0152 mm / ~0.017 mm).

2. **JLC06161H-7628 (Standard Economical / Thick Prepreg ~0.21 mm)**
   * Target: General-purpose multi-layer boards, wider impedance traces.
   * L1-to-L2 Prepreg: 7628 (~0.2104 mm, $\varepsilon_r \approx 4.4-4.6$).
   * Core L2-L3: 0.40 mm ($\varepsilon_r \approx 4.5-4.6$).
   * Prepreg L3-L4: 7628 (~0.2028 mm, $\varepsilon_r \approx 4.5-4.6$).
   * Core L4-L5: 0.40 mm ($\varepsilon_r \approx 4.5-4.6$).
   * Prepreg L5-L6: 7628 (~0.2104 mm, $\varepsilon_r \approx 4.4-4.6$).
   * Copper Weight: Outer 1 oz (0.035 mm finished), Inner 0.5 oz (0.0152 mm).

*Default Recommendation for CM5 AI Camera Board*: **JLC06161H-3313**, as the current `CM5-AI-Cam-CopperPilot.kicad_pcb` uses 0.1 mm outer dielectric and Hirose 0.4 mm pitch DF40 connectors require narrow trace widths to escape.

---

## 2. JLCPCB 6-Layer Fabrication Constraints

| Parameter | JLCPCB Absolute Limit | Recommended Standard DFM | KiCad `.kicad_pro` Setting | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Minimum Trace Width** | 0.09 mm (3.5 mil) | 0.127 mm (5.0 mil) | `0.09 mm` (limit), `0.15 mm` (default) | 0.09 mm is JLCPCB multi-layer limit; 0.127 mm ensures high yield |
| **Minimum Trace Clearance** | 0.09 mm (3.5 mil) | 0.127 mm (5.0 mil) | `0.10 mm` (min_clearance) | 0.127 mm (5 mil) recommended for general nets |
| **Minimum Via Drill (Hole)** | 0.15 mm (6.0 mil) | 0.30 mm (12.0 mil) | `0.20 mm` (min_through_hole_diameter) | 0.15 mm incurs advanced process fee; 0.20–0.30 mm standard |
| **Minimum Via Pad Diameter** | 0.25 mm (10.0 mil) | 0.50 mm (20.0 mil) | `0.40 mm` (min_via_diameter) | Pad $\ge$ Drill + 0.20 mm ensures $\ge$ 0.10 mm annular ring |
| **Minimum Annular Ring** | 0.05 mm (2.0 mil) | 0.10 mm (4.0 mil) | `0.10 mm` (min_via_annular_width) | Absolute minimum 0.05 mm for laser/microvia; 0.10 mm for mechanical PTH |
| **Hole-to-Hole Spacing (PTH-PTH)** | 0.50 mm (20 mil) | 0.50 mm (20 mil) | `0.50 mm` (min_hole_to_hole) | Drill hole edge to drill hole edge; prevents breakout/cracking |
| **Hole-to-Hole Spacing (Via-Via)** | 0.254 mm (10 mil) | 0.30 mm (12 mil) | `0.254 mm` (custom DRC / via rule) | Hole edge to hole edge for same or different nets |
| **Drill-to-Copper Clearance** | 0.254 mm (10 mil) | 0.30 mm (12 mil) | `0.254 mm` (min_hole_clearance) | Hole edge to unrelated trace or copper polygon |
| **Copper to Board Edge (Routed)** | 0.30 mm (12 mil) | 0.40–0.50 mm (16–20 mil) | `0.50 mm` (min_copper_edge_clearance) | CNC milling routing tolerance is $\pm 0.20$ mm |
| **Copper to Board Edge (V-Cut)** | 0.40 mm (16 mil) | 0.50–0.80 mm (20–32 mil) | `0.50 mm` | V-groove scoring tolerance is $\pm 0.40$ mm |
| **Solder Mask Dam (Green)** | 0.08 mm (3.15 mil) | 0.10 mm (4.0 mil) | `0.08 mm` (solder_mask_bridge) | Dams $< 0.08$ mm will be stripped by fab (ganged mask opening) |
| **Solder Mask Dam (Non-Green)** | 0.10 mm (4.0 mil) | 0.12 mm (4.7 mil) | `0.10 mm` | Applies to Black, White, Blue, Red, Yellow, Purple masks |
| **Solder Mask Expansion** | 0.00 mm (1:1 CAD) | 0.00 mm or 0.03 mm | `0.00 mm` (pad_to_mask_clearance) | JLCPCB CAM automatically applies 0.038 mm expansion if 0 |
| **Silkscreen Min Line Width** | 0.15 mm (6.0 mil) | 0.18–0.20 mm (7–8 mil) | `0.15 mm` (min_text_thickness) | Lines $< 0.15$ mm will not resolve or break during screen printing |
| **Silkscreen Min Text Height** | 0.80 mm (32 mil) | 1.00 mm (40 mil) | `0.80 mm` (min_text_height) | 1.0 mm height / 0.18 mm line width gives clear legibility |
| **Silkscreen-to-Pad Clearance** | 0.15 mm (6.0 mil) | 0.20 mm (8.0 mil) | `0.15 mm` (min_silk_clearance) | JLCPCB clips silkscreen on pads; margin prevents truncated text |

---

## 3. Controlled Impedance Modeling & Net Class Specifications

### 3.1 Controlled Impedance Targets for CM5 Carrier

The CM5 carrier board routes several multi-gigabit differential interfaces:
* **USB 2.0 High-Speed / USB 3.0 SuperSpeed**: $90\ \Omega \pm 10\%$ differential.
* **Gigabit Ethernet (RGMII / 1000BASE-T)**: $100\ \Omega \pm 10\%$ differential.
* **PCIe Gen 2 / Gen 3**: $100\ \Omega \pm 10\%$ (or $85\ \Omega$ for PCIe, but $100\ \Omega$ is standard for CM5 carrier compatible PCIe x1 slots).
* **MIPI CSI-2 / DSI (Camera & Display)**: $100\ \Omega \pm 10\%$ differential.
* **HDMI TMDS Clock & Data**: $100\ \Omega \pm 10\%$ differential.
* **Single-Ended RF / Clocks / Critical Signals**: $50\ \Omega \pm 10\%$.

### 3.2 Stackup A: JLC06161H-3313 (Recommended for CM5 Board)

Dielectric height $h = 0.0994\ \text{mm}$, $\varepsilon_r = 4.10$, copper thickness $t = 0.035\ \text{mm}$ (outer L1/L6 over L2/L5 ground):

| Net Class | Target Impedance | Trace Width ($W$) | Differential Gap ($S$) | Clearance ($C$) | Via Size (Pad / Drill) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Default** | Non-critical digital | 0.150 mm (5.9 mil) | N/A | 0.150 mm | 0.50 mm / 0.30 mm |
| **Power** | Power distribution | 0.500 mm (20 mil) | N/A | 0.200 mm | 0.65 mm / 0.35 mm |
| **HighSpeed_90R** | $90\ \Omega \pm 10\%$ Diff (USB) | **0.125 mm (4.9 mil)** | **0.127 mm (5.0 mil)** | 0.150 mm | 0.45 mm / 0.25 mm |
| **HighSpeed_100R** | $100\ \Omega \pm 10\%$ Diff (MIPI/ETH/PCIE) | **0.105 mm (4.1 mil)** | **0.150 mm (5.9 mil)** | 0.150 mm | 0.45 mm / 0.25 mm |
| **SingleEnded_50R** | $50\ \Omega \pm 10\%$ Single-Ended | **0.165 mm (6.5 mil)** | N/A | 0.250 mm | 0.45 mm / 0.25 mm |

*Calculated Impedance Verification:*
* `HighSpeed_90R`: $W = 0.125\ \text{mm}, S = 0.127\ \text{mm} \implies Z_{\text{diff}} \approx 91.2\ \Omega$ (Within $1.3\%$ of target).
* `HighSpeed_100R`: $W = 0.105\ \text{mm}, S = 0.150\ \text{mm} \implies Z_{\text{diff}} \approx 99.8\ \Omega$ (Within $0.2\%$ of target).
* `SingleEnded_50R`: $W = 0.165\ \text{mm} \implies Z_0 \approx 50.4\ \Omega$ (Within $0.8\%$ of target).

### 3.3 Stackup B: JLC06161H-7628 (Alternative Economical Stackup)

Dielectric height $h = 0.2104\ \text{mm}$, $\varepsilon_r = 4.45$, copper thickness $t = 0.035\ \text{mm}$ (outer L1/L6 over L2/L5 ground):

| Net Class | Target Impedance | Trace Width ($W$) | Differential Gap ($S$) | Clearance ($C$) | Via Size (Pad / Drill) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Default** | Non-critical digital | 0.200 mm (8.0 mil) | N/A | 0.200 mm | 0.50 mm / 0.30 mm |
| **Power** | Power distribution | 0.600 mm (24 mil) | N/A | 0.250 mm | 0.70 mm / 0.40 mm |
| **HighSpeed_90R** | $90\ \Omega \pm 10\%$ Diff (USB) | **0.250 mm (9.8 mil)** | **0.150 mm (5.9 mil)** | 0.200 mm | 0.50 mm / 0.25 mm |
| **HighSpeed_100R** | $100\ \Omega \pm 10\%$ Diff (MIPI/ETH/PCIE) | **0.175 mm (6.9 mil)** | **0.150 mm (5.9 mil)** | 0.200 mm | 0.50 mm / 0.25 mm |
| **SingleEnded_50R** | $50\ \Omega \pm 10\%$ Single-Ended | **0.340 mm (13.4 mil)** | N/A | 0.300 mm | 0.50 mm / 0.25 mm |

---

## 4. Double-Sided SMT Assembly DFM Rules

JLCPCB supports double-sided SMT assembly with automated pick-and-place and dual-reflow soldering ovens.

### 4.1 Process Rails and Tooling Holes

1. **Process Edge / Rail Width**:
   * Minimum width: **5.0 mm** along two longer opposite parallel edges.
   * Rails are mandatory for double-sided SMT assembly to support conveyor clamping without contacting bottom-side components.
2. **Tooling (Positioning) Holes**:
   * Type: Non-Plated Through Hole (NPTH).
   * Diameter: **2.00 mm** ($\pm 0.05$ mm) (standard JLCPCB specification; 1.152 mm also accepted).
   * Quantity: 3 or 4 holes located in the process rails outside the finished PCB outline.
   * Location: Offset **5.0 mm** from board corners, **3.85 mm** from the rail outer edge.
   * Clearance: No copper or silkscreen within **1.0 mm** around tooling holes.

### 4.2 Fiducial Specifications

1. **Global Fiducials**:
   * Quantity: Minimum **3 global fiducials per side** (top and bottom), arranged asymmetrically (L-shape pattern) to detect 180° inversion.
   * Copper Pad Diameter: **1.0 mm** circular bare copper pad (with ENIG or HASL surface finish).
   * Solder Mask Opening: **2.0 mm** diameter circular opening (provides 0.5 mm concentric annular mask clearance).
   * Keep-Out Zone: **3.0 mm** minimum diameter keep-out around the fiducial center (no traces, vias, ground copper, or silkscreen).
   * Position: Offset **3.85 mm** from panel/board edge; must not overlap V-cuts or stamp holes.
2. **Local Fiducials**:
   * Required for fine-pitch parts: BGA ($\text{pitch} \le 0.8$ mm), QFN ($\text{pitch} \le 0.5$ mm), and Hirose DF40 high-density B2B connectors.
   * Configuration: 2 diagonal fiducials placed outside opposing corners of the footprint.
   * Dimensions: 0.8 mm or 1.0 mm copper pad, 1.6 mm or 2.0 mm mask opening, 2.5 mm keep-out.

### 4.3 Component Spacing and Clearances

1. **SMD Component-to-Component Spacing**:
   * Passive to Passive (0402 / 0603): Body-to-body $\ge 0.35$ mm; Pad-to-pad $\ge 0.20$ mm.
   * IC to Passive: Body-to-body $\ge 0.50$ mm (facilitates optical inspection and hot-air rework).
   * IC to IC (QFP, QFN, SOIC): Body-to-body $\ge 0.80$ mm.
   * BGA to Surrounding Components: Keep at least **1.0 mm to 1.5 mm** clearance from BGA courtyard to permit routing escapes and rework nozzle access.
2. **Component Distance to Board Edges**:
   * Milled / Routed Board Edge: Component body $\ge 0.50$ mm; Pad $\ge 0.50$ mm.
   * V-Cut Scoring Line: Component body $\ge 1.00$ mm; Multilayer Ceramic Capacitors (MLCC) $\ge 1.50$–$2.00$ mm oriented parallel to the V-cut groove (prevents bending stress and micro-cracking during depaneling).
   * Process Rail Margin: All components must reside inside the PCB Edge.Cuts boundary (0 mm penetration into the 5.0 mm rail).

### 4.4 Secondary (Bottom) Side Reflow Constraints

During double-sided SMT:
1. **Reflow Sequence**: The primary side (typically top side, holding heavier, taller, and higher-thermal-mass components) is populated and reflowed first. The board is flipped, and the secondary (bottom) side is populated and reflowed.
2. **Bottom-Side Component Retention (Surface Tension Rule)**:
   * During the second reflow pass, bottom-side components hang inverted in molten solder. They are held in place solely by solder surface tension.
   * Weight Limit Criterion:
     $$\frac{\text{Component Mass (g)}}{\text{Total Solder Pad Contact Area } (\text{in}^2)} \le 30\ \text{g/in}^2 \quad \left(\approx 0.0465\ \text{g/mm}^2\right)$$
   * Practical Guideline: Any individual component heavier than **5 grams** must be placed on the primary (top) side or glued with SMT adhesive.
   * Keep heavy parts (electrolytic capacitors, transformers, inductors $> 6\times 6$ mm, heavy connectors, heatsinks) exclusively on the top side.
3. **Bottom-Side Component Height Limit**:
   * Maximum component height on bottom side: **$\le 3.0$ mm** (standard JLCPCB reflow carrier clearance).
   * Taller components can collide with reflow fixtures, conveyor belts, or wave solder pallets.

---

## 5. Direct `.kicad_pro` Configuration Mapping

Below are the exact JSON fragments to insert into `CM5-AI-Cam-CopperPilot.kicad_pro` to enforce these rules.

### 5.1 `board.design_settings.rules`

```json
{
  "board": {
    "design_settings": {
      "rules": {
        "max_error": 0.005,
        "min_clearance": 0.10,
        "min_connection": 0.0,
        "min_copper_edge_clearance": 0.50,
        "min_groove_width": 0.0,
        "min_hole_clearance": 0.254,
        "min_hole_to_hole": 0.50,
        "min_microvia_diameter": 0.20,
        "min_microvia_drill": 0.10,
        "min_resolved_spokes": 2,
        "min_silk_clearance": 0.15,
        "min_text_height": 0.80,
        "min_text_thickness": 0.15,
        "min_through_hole_diameter": 0.20,
        "min_track_width": 0.09,
        "min_via_annular_width": 0.10,
        "min_via_diameter": 0.40,
        "solder_mask_to_copper_clearance": 0.00,
        "use_height_for_length_calcs": true
      }
    }
  }
}
```

### 5.2 `board.design_settings.rule_severities`

Ensure key DFM failure modes are caught as DRC errors rather than warnings:

```json
{
  "board": {
    "design_settings": {
      "rule_severities": {
        "annular_width": "error",
        "clearance": "error",
        "copper_edge_clearance": "error",
        "drill_out_of_range": "error",
        "hole_clearance": "error",
        "hole_to_hole": "error",
        "holes_co_located": "warning",
        "solder_mask_bridge": "error",
        "silk_edge_clearance": "warning",
        "silk_over_copper": "warning",
        "text_height": "warning",
        "text_thickness": "warning",
        "track_width": "error"
      }
    }
  }
}
```

### 5.3 `net_settings.classes` (For JLC06161H-3313 Stackup)

```json
{
  "net_settings": {
    "classes": [
      {
        "bus_width": 12,
        "clearance": 0.15,
        "diff_pair_gap": 0.25,
        "diff_pair_via_gap": 0.25,
        "diff_pair_width": 0.20,
        "line_style": 0,
        "microvia_diameter": 0.30,
        "microvia_drill": 0.10,
        "name": "Default",
        "pcb_color": "rgba(0, 0, 0, 0.000)",
        "priority": 2147483647,
        "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.15,
        "tuning_profile": "",
        "via_diameter": 0.50,
        "via_drill": 0.30,
        "wire_width": 6
      },
      {
        "bus_width": 12,
        "clearance": 0.20,
        "diff_pair_gap": 0.25,
        "diff_pair_via_gap": 0.25,
        "diff_pair_width": 0.50,
        "line_style": 0,
        "microvia_diameter": 0.30,
        "microvia_drill": 0.10,
        "name": "Power",
        "pcb_color": "rgba(200, 50, 50, 0.800)",
        "priority": 100,
        "schematic_color": "rgba(200, 50, 50, 0.800)",
        "track_width": 0.50,
        "tuning_profile": "",
        "via_diameter": 0.65,
        "via_drill": 0.35,
        "wire_width": 12
      },
      {
        "bus_width": 12,
        "clearance": 0.15,
        "diff_pair_gap": 0.127,
        "diff_pair_via_gap": 0.15,
        "diff_pair_width": 0.125,
        "line_style": 0,
        "microvia_diameter": 0.30,
        "microvia_drill": 0.10,
        "name": "HighSpeed_90R",
        "pcb_color": "rgba(0, 150, 200, 0.800)",
        "priority": 50,
        "schematic_color": "rgba(0, 150, 200, 0.800)",
        "track_width": 0.125,
        "tuning_profile": "",
        "via_diameter": 0.45,
        "via_drill": 0.25,
        "wire_width": 6
      },
      {
        "bus_width": 12,
        "clearance": 0.15,
        "diff_pair_gap": 0.15,
        "diff_pair_via_gap": 0.15,
        "diff_pair_width": 0.105,
        "line_style": 0,
        "microvia_diameter": 0.30,
        "microvia_drill": 0.10,
        "name": "HighSpeed_100R",
        "pcb_color": "rgba(180, 50, 220, 0.800)",
        "priority": 40,
        "schematic_color": "rgba(180, 50, 220, 0.800)",
        "track_width": 0.105,
        "tuning_profile": "",
        "via_diameter": 0.45,
        "via_drill": 0.25,
        "wire_width": 6
      }
    ]
  }
}
```

---

## 6. KiCad Custom DRC Rules (`.kicad_dru`) for JLCPCB

KiCad 7/8/9/10 supports `.kicad_dru` custom syntax to enforce rules beyond simple global parameters:

```kicad_dru
# JLCPCB 6-Layer Specific Custom Design Rules

(version 1)

# Rule 1: Via-to-Via Hole Clearance (0.254 mm edge-to-edge)
(rule "Via_Hole_To_Via_Hole"
   (constraint hole_to_hole (min 0.254mm))
   (condition "A.type == 'Via' && B.type == 'Via'"))

# Rule 2: Through-Hole Pad to Through-Hole Pad (0.50 mm edge-to-edge)
(rule "PTH_To_PTH_Hole"
   (constraint hole_to_hole (min 0.50mm))
   (condition "A.type == 'Pad' && B.type == 'Pad' && A.pad_type == 'Through-hole' && B.pad_type == 'Through-hole'"))

# Rule 3: High-Speed Differential Pairs Clearance to Other Copper (3W Rule)
(rule "Diff_Pair_Isolation_3W"
   (constraint clearance (min 0.30mm))
   (condition "A.NetClass == 'HighSpeed_90R' || A.NetClass == 'HighSpeed_100R'")
   (condition "!(B.NetClass == 'HighSpeed_90R' || B.NetClass == 'HighSpeed_100R')"))

# Rule 4: Board Edge Clearance for V-Cut / Scoring Regions
(rule "Board_Edge_Copper_Clearance"
   (constraint edge_clearance (min 0.50mm))
   (condition "A.Layer == '*.Cu'"))
```

---

## 7. Recommended Net-to-Class Assignment Mapping for CM5 AI Camera

| Schematic Net Name Patterns | Assigned Net Class | Target Constraint |
| :--- | :--- | :--- |
| `+5V`, `+5V_IN`, `+5V_SYS`, `+3V3`, `+1V8`, `+1V1`, `GND`, `VBUS*` | **Power** | Width: 0.50 mm, Clearance: 0.20 mm, Via: 0.65/0.35 mm |
| `USB_D+`, `USB_D-`, `USB2_*`, `USB3_*_TX_*`, `USB3_*_RX_*` | **HighSpeed_90R** | $W=0.125$ mm, $S=0.127$ mm ($90\ \Omega$ diff) |
| `ETH_TX*`, `ETH_RX*`, `ETH_TRD*` | **HighSpeed_100R** | $W=0.105$ mm, $S=0.150$ mm ($100\ \Omega$ diff) |
| `PCIE_TX*`, `PCIE_RX*`, `PCIE_CLK*` | **HighSpeed_100R** | $W=0.105$ mm, $S=0.150$ mm ($100\ \Omega$ diff) |
| `CAM0_D*`, `CAM0_CLK*`, `CAM1_D*`, `CAM1_CLK*` (MIPI CSI-2) | **HighSpeed_100R** | $W=0.105$ mm, $S=0.150$ mm ($100\ \Omega$ diff) |
| `HDMI_D*`, `HDMI_CLK*` (HDMI TMDS) | **HighSpeed_100R** | $W=0.105$ mm, $S=0.150$ mm ($100\ \Omega$ diff) |
| All other GPIOs, I2C, SPI, UART, Controls | **Default** | Width: 0.15 mm, Clearance: 0.15 mm, Via: 0.50/0.30 mm |
