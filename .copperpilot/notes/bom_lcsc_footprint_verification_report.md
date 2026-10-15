# Comprehensive BOM, LCSC Sourcing, and Footprint Verification Report

**Project:** CM5 AI Camera Carrier Board (`CM5-AI-Cam-CopperPilot`)  
**Target Assembler:** JLCPCB PCBA / SMT Assembly  
**Audited Artifacts:**
- BOM: `jlcpcb_production/assembly/bom_jlcpcb.csv` (42 lines, 81 placed instances)
- CPL: `jlcpcb_production/assembly/cpl_jlcpcb.csv` (81 placed instances)
- Schematic: `CM5-AI-Cam-CopperPilot.kicad_sch` (91 non-power symbol instances)
- PCB: `CM5-AI-Cam-CopperPilot.kicad_pcb` (90 placed footprint instances)
- Footprint Library: `./CM5.pretty/` (63 footprint definitions)

---

## 1. Fatal Footprint Package Mismatches

Four critical components have fatal mechanical or land pattern incompatibilities between the physical component, the BOM part number, and the placed PCB footprint:

### 1.1 U5: MP1658GTF-Z (Buck Converter)
- **Schematic Reference / Value:** `U5`, `MP1658GTF-Z` (LCSC `C9900009837`)
- **Assigned PCB Footprint:** `CM5:TSOT-23-6`
- **Datasheet Reality:** Monolithic Power Systems (MPS) package code `GTF` is strictly **SOT-563** (1.60 × 1.20 mm body, 1.60 × 1.60 mm total footprint with leads, 0.50 mm lead pitch).
- **Physical Comparison:**
  | Dimension | MP1658GTF-Z (SOT-563) | Placed Footprint (TSOT-23-6) | Conflict Severity |
  |:---|:---|:---|:---|
  | **Lead Pitch** | 0.50 mm | 0.95 mm | **+90% pitch error** |
  | **Pad Center Span (X)** | 1.425 mm | 2.275 mm | **+0.85 mm excessive span** |
  | **Pad Dimensions** | 0.675 × 0.35 mm | 1.325 × 0.60 mm | **Massive oversize** |
- **Assembly Consequence:** The physical SOT-563 IC leads fall entirely into the central dead space between the TSOT-23-6 pads. The component cannot bridge the pads, making automated SMT or hand soldering impossible.
- **Remediation:** Replace footprint with `CM5:SOT-563` (already existing in `./CM5.pretty/SOT-563.kicad_mod`).

### 1.2 Q1, Q2: DMG1012T-7 (I2C Level-Shifter MOSFETs)
- **Schematic Reference / Value:** `Q1, Q2`, `DMG1012T` (LCSC `C20512`)
- **Assigned PCB Footprint:** `CM5:Texas_DRT-3`
- **Datasheet Reality:** Diodes Inc `DMG1012T-7` is packaged strictly in **SOT-523** (body 1.60 × 0.80 mm, overall span 1.60 mm, lead pitch 1.00 mm). The suffix `T` in Diodes Inc parts designates SOT-523.
- **Physical Comparison:**
  | Dimension | DMG1012T-7 (SOT-523) | Placed Footprint (Texas_DRT-3) | Conflict Severity |
  |:---|:---|:---|:---|
  | **Lead Pitch (P1-P2)** | 1.00 mm | 0.70 mm | **+43% pitch error** |
  | **Pad Span (Y)** | 1.29 mm | 0.85 mm | **+0.44 mm mismatch** |
  | **Pad Dimensions** | 0.51 × 0.40 mm | 0.30 × 0.30 mm | **Pads ~50% undersized** |
  | **Component Body** | 1.60 × 1.60 mm | 1.00 × 0.80 mm | **Part 1.6× larger than footprint** |
- **Assembly Consequence:** The physical SOT-523 transistor is ~160% the size of the Texas_DRT-3 land pattern. Solder paste will bridge across the minute 0.3 mm pads, or the transistor pins will hang outside the pads with zero solder fillet.
- **Remediation:** Replace footprint with `CM5:SOT-523` (already existing in `./CM5.pretty/SOT-523.kicad_mod`).

### 1.3 J2: USB-A Host Connector (Vertical vs Right-Angle)
- **Schematic Reference / Value:** `J2`, `USB_A_Vertical`
- **Assigned PCB Footprint:** `CM5:MOLEX_USB_67298-4090` (Vertical through-hole, Molex 105057-0001 equivalent)
- **Assigned BOM Part:** `C720523` -> **XUNPU USB-226-BRY**
- **Datasheet Reality:** XUNPU USB-226-BRY is a **Right-Angle (side-insertion)** through-hole USB-A receptacle. The PCB footprint is a **Vertical (top-insertion)** through-hole receptacle.
- **Physical Comparison:**
  | Feature | BOM Part (XUNPU USB-226-BRY) | PCB Footprint (MOLEX 67298-4090) |
  |:---|:---|:---|
  | **Insertion Axis** | Horizontal (Right-Angle) | Vertical (Straight) |
  | **Signal Pins** | 4 pins bent 90° | 4 straight pins inline at Y=0 (pitch 2.0/2.5 mm) |
  | **Shield Tabs** | 2 lateral side snap-in tabs | 3 triangular retention tabs (X=-3.07, +3.50, +10.07 mm) |
- **Assembly Consequence:** The pins and mechanical retention legs of the right-angle connector cannot mechanically align or insert into the vertical mounting holes on the PCB.
- **Remediation:** Update BOM to a genuine vertical through-hole USB-A connector (e.g. LCSC `C698207` or Molex `105057-0001`), or assign through-hole manual assembly with the correct vertical part.

### 1.4 Module1: Raspberry Pi Compute Module 5 Connector (CPL & BOM Multiplicity Defect)
- **Schematic Reference / Value:** `Module1`, `ComputeModule5-CM5`
- **Assigned PCB Footprint:** `CM5:Raspberry-Pi-5-Compute-Module` (200-pin monolithic footprint)
- **Assigned BOM Part:** `C597931` -> **Hirose DF40C-100DS-0.4V(51)** (Quantity = 1)
- **Datasheet Reality:** The Raspberry Pi CM5 requires **TWO independent 100-pin Hirose DF40 mezzanine connectors** separated by 33.92 mm center-to-center.
- **Assembly Consequence:**
  1. **BOM Shortage:** The BOM lists Quantity 1 of `C597931`, leaving the second 100-pin socket completely unpopulated.
  2. **CPL Centroid Collision:** Because `Module1` is a single monolithic KiCad component, `cpl_jlcpcb.csv` exports a single centroid at (72.8000, -61.4200) on B.Cu. This position corresponds to the dead air gap between the two connectors! An automated pick-and-place machine will attempt to drop a single 100-pin connector into the center void.
- **Remediation:** Split `Module1` into two schematic symbols and footprints (`J1A`, `J1B`) using `CM5:CONN_DF40C-100DS-0.4V51_HIR`. This automatically yields Quantity 2 of `C597931` in the BOM and two accurate placement centroids in the CPL.

---

## 2. BOM LCSC Part Number Verification

Verification of all 42 lines in `jlcpcb_production/assembly/bom_jlcpcb.csv` against component datasheets, pinout, and JLCPCB library:

| Row | Comment / Value | Designators | Qty | Assigned Footprint | LCSC Part # | Manufacturer & MPN | JLCPCB Class | Verification Status & Findings |
|:---:|:---|:---|:---:|:---|:---|:---|:---:|:---|
| 1 | 2.2uF | C1, C12, C5 | 3 | C_0402_1005Metric | C23733 | Samsung CL05A225MP5NRNC | Basic | **VERIFIED MATCH** (2.2uF 10V X5R 0402) |
| 2 | 100nF | C10, C14, C3 | 3 | C_0402_1005Metric | C1525 | Samsung CL05B104KO5NNNC | Basic | **VERIFIED MATCH** (100nF 50V X7R 0402) |
| 3 | 10uF | C11, C22, C4 | 3 | C_0805_2012Metric | C15850 | Samsung CL21A106KAYNNNE | Basic | **VERIFIED MATCH** (10uF 25V X5R 0805) |
| 4 | 1uF | C15, C16, C2, C21, C29, C30, C6, C7, C8, C9 | 10 | C_0402_1005Metric | C52923 | Samsung CL05A105KA5NQNC | Basic | **VERIFIED MATCH** (1uF 25V X5R 0402) |
| 5 | 0.1uF | C17, C18, C23, C24, C27, C28, C31, C32 | 8 | C_0402_1005Metric | C1525 | Samsung CL05B104KO5NNNC | Basic | **VERIFIED MATCH** (0.1uF 50V X7R 0402) |
| 6 | 10pF | C20 | 1 | C_0402_1005Metric | C32949 | Samsung CL05C100JB5NNNC | Basic | **VERIFIED MATCH** (10pF 50V C0G 0402) |
| 7 | 22uF | C25, C26 | 2 | C_0805_2012Metric | C45783 | Samsung CL21A226MAQNNNE | Extended | **VERIFIED MATCH** (22uF 25V X5R 0805) |
| 8 | DSI_15P | DSI1 | 1 | Molex_200528-0150_1x15-1MP_P1.00mm_Horizontal | C2914074 | HDGC 1.0K-FX-15PWB / Molex 200528-0150 | Extended | **VERIFIED MATCH** (15P 1.0mm pitch FPC) |
| 9 | 120R | FB1 | 1 | R_0603_1608Metric | C50843 | Fenghua CBG160808U121T | Basic | **VERIFIED MATCH** (120Ω @ 100MHz 0603 Bead) |
| 10 | Conn_01x03 | H3, H4, H5 | 3 | PinHeader_1x03_P2.54mm_Vertical | C49257 | BOOMELE 2.54-1*3P | Extended | **VERIFIED MATCH** (Requires TH hand assembly) |
| 11 | HDMI_Mini_C | HDMI1 | 1 | HDMI_Mini-C_Molex_47151-0001 | C2013978 | TE Connectivity 2013978-2 / Molex 47151-0001 | Extended | **SOURCING RISK** (Molex 47151-0001 obsolete; C2013978 out of stock) |
| 12 | IMX219_30P | J1 | 1 | Camera_Module_IMX219-D160 | C6539772 | Hirose DF37NB-30DS-0.4V(75) | Extended | **VERIFIED MATCH** (30P 0.4mm pitch mezzanine) |
| 13 | USB_A_Vertical | J2 | 1 | MOLEX_USB_67298-4090 | C720523 | XUNPU USB-226-BRY | Extended | **FATAL MISMATCH** (BOM is Right-Angle; Footprint is Vertical TH) |
| 14 | SW_Push_SPST | Key1 | 1 | SW_SPST_PTS645Sx43SMTR92 | C318884 | C&K PTS645SM43SMTR92 / TS-1088R | Extended | **VERIFIED MATCH** (6×6mm SMD tactile switch) |
| 15 | MCF1210BF2-900T01 | L1, L2, L3 | 3 | L_CommonModeChoke_Coilank_ACM1210 | C49073870 | Coilank ACM1210-900-2P-T01 | Extended | **VERIFIED MATCH** (90Ω @ 100MHz 1210/0504) |
| 16 | LED Red | L5 | 1 | LED_0603_1608Metric | C2286 | Everlight 19-217/R6C-AL1M2VY/3T | Basic | **VERIFIED MATCH** (0603 Red LED) |
| 17 | LED Green | L6 | 1 | LED_0603_1608Metric | C72043 | Everlight 19-217/GHC-YR1S2/3T | Extended | **VERIFIED MATCH** (0603 Emerald Green LED) |
| 18 | 4.7uH | L7 | 1 | L_Bourns_SRP5030CC | C840574 | Taiyo Yuden NRS5030T4R7MMGJ / Bourns SRP5030CC | Extended | **VERIFIED MATCH** (4.7µH 5×5mm shielded inductor) |
| 19 | ComputeModule5-CM5 | Module1 | 1 | Raspberry-Pi-5-Compute-Module | C597931 | Hirose DF40C-100DS-0.4V(51) | Extended | **FATAL CPL/BOM DEFECT** (Needs Qty 2 & dual centroids) |
| 20 | Raspberry_Pi_40Pin_GPIO | PI1 | 1 | PinHeader_2x20_P2.54mm_Vertical | C50980 | BOOMELE 2.54-2*20P | Extended | **VERIFIED MATCH** (Requires TH hand assembly) |
| 21 | DMG1012T | Q1, Q2 | 2 | Texas_DRT-3 | C20512 | Diodes Inc DMG1012T-7 | Basic | **FATAL MISMATCH** (Part is SOT-523; Footprint is TI DRT-3) |
| 22 | 22R | R10 | 1 | R_0402_1005Metric | C25092 | Uni-Ohm 0402WGF220JTCE | Basic | **VERIFIED MATCH** (22Ω 1% 0402) |
| 23 | 10k | R11, R14, R30, R34 | 4 | R_0402_1005Metric | C25744 | Uni-Ohm 0402WGF1002TCE | Basic | **VERIFIED MATCH** (10kΩ 1% 0402) |
| 24 | 1k | R12, R13 | 2 | R_0402_1005Metric | C11702 | Uni-Ohm 0402WGF1001TCE | Basic | **VERIFIED MATCH** (1kΩ 1% 0402) |
| 25 | 100k | R15, R19 | 2 | R_0402_1005Metric | C25741 | Uni-Ohm 0402WGF1003TCE | Basic | **VERIFIED MATCH** (100kΩ 1% 0402) |
| 26 | 10R | R16 | 1 | R_0402_1005Metric | C25077 | Uni-Ohm 0402WGF100JTCE | Basic | **VERIFIED MATCH** (10Ω 1% 0402) |
| 27 | 0R | R17, R22, R24 | 3 | R_0402_1005Metric | C17168 | Uni-Ohm 0402WGF0000TCE | Basic | **VERIFIED MATCH** (Note: R1 and R29 omitted from BOM) |
| 28 | 5.1k | R2, R3 | 2 | R_0402_1005Metric | C25905 | Uni-Ohm 0402WGF5101TCE | Basic | **VERIFIED MATCH** (5.1kΩ 1% 0402 Type-C CC) |
| 29 | 61.9k | R20 | 1 | R_0402_1005Metric | C25916 | Uni-Ohm 0402WGF6192TCE | Basic | **VERIFIED MATCH** (61.9kΩ 1% 0402 MP1658 FB) |
| 30 | 20k | R21 | 1 | R_0402_1005Metric | C25765 | Uni-Ohm 0402WGF2002TCE | Basic | **VERIFIED MATCH** (20kΩ 1% 0402 MP1658 FB) |
| 31 | 47k | R28 | 1 | R_0402_1005Metric | C25792 | Uni-Ohm 0402WGF4702TCE | Basic | **VERIFIED MATCH** (47kΩ 1% 0402) |
| 32 | 4.7k | R4, R7 | 2 | R_0402_1005Metric | C25900 | Uni-Ohm 0402WGF4701TCE | Basic | **VERIFIED MATCH** (Note: R35 omitted from BOM) |
| 33 | 2.2k | R5, R8 | 2 | R_0402_1005Metric | C25879 | Uni-Ohm 0402WGF2201TCE | Basic | **VERIFIED MATCH** (2.2kΩ 1% 0402) |
| 34 | Micro_SD_Card_Det | TF1 | 1 | SDCARD_MOLEX_503398-1892 | C91145 | Korean Hroparts TF-01A | Basic | **VERIFIED MATCH** (Push-Push MicroSD Socket) |
| 35 | RT9193-28GB | U1 | 1 | SOT-23-5 | C114059 | Shanghai Belling BL9193-28BAPRN | Extended | **VERIFIED MATCH** (2.8V 300mA LDO) |
| 36 | RT9193-18GB | U2 | 1 | SOT-23-5 | C27416 | Richtek RT9193-18GB | Extended | **VERIFIED MATCH** (1.8V 300mA LDO) |
| 37 | RT9013-12 | U3 | 1 | SOT-23-5 | C7434207 | Richtek RT9013-12GB | Extended | **VERIFIED MATCH** (1.2V 500mA LDO) |
| 38 | DIO7003HCST5 | U4, U7 | 2 | SOT-23-5 | C157437 | STMicroelectronics STMPS2171STR | Extended | **COMMENT MISMATCH** (BOM comment DIO7003 vs part STMPS2171; pinout matches) |
| 39 | MP1658GTF-Z | U5 | 1 | TSOT-23-6 | C9900009837 | Monolithic Power Systems MP1658GTF-Z | Special | **FATAL MISMATCH** (Part is SOT-563; Footprint is TSOT-23-6) |
| 40 | FSUSB42MX | U6 | 1 | UQFN-10_1.4x1.8mm_P0.4mm | C11145 | onsemi FSUSB42UMX | Extended | **VERIFIED MATCH** (UQFN-10 1.4×1.8mm USB switch) |
| 41 | STMPS2171STR | U8 | 1 | SOT-23-5 | C157437 | STMicroelectronics STMPS2171STR | Extended | **VERIFIED MATCH** (1A SOT-23-5 USB Power Switch) |
| 42 | OSC_24MHz | X1 | 1 | Crystal_SMD_3225-4Pin_3.2x2.5mm | C717686 | Yangxing Tech OT322524MJBA4SL | Extended | **VERIFIED MATCH** (24.000 MHz 1.8V Active OSC) |

---

## 3. Missing / DNP Component Status

### 3.1 Active Components Omitted from BOM (Critical Assembly Flaws)
Three components are active, non-DNP circuit elements (`(dnp no)`, `(in_bom yes)` in schematic and PCB), but were completely omitted from `jlcpcb_production/assembly/bom_jlcpcb.csv`:

1. **R1 (0Ω 0402, LCSC C17168):**
   - **Net Connections:** Pad 1 connects to `/SD_VDD_Override`, Pad 2 connects to `GND`.
   - **Circuit Function:** Pulls `/SD_VDD_Override` low to configure the SD card power switch logic for the Compute Module 5.
   - **Consequence of Omission:** Control line `/SD_VDD_Override` will float, leading to unpredictable SD card power rail switching and card detection failures.
2. **R29 (0Ω 0402, LCSC C17168):**
   - **Net Connections:** Pad 1 connects to `/EEPROM_WP`, Pad 2 connects to `GND`.
   - **Circuit Function:** Ties the CM5 baseboard EEPROM write-protect line to ground, enabling write protection or active configuration.
   - **Consequence of Omission:** `/EEPROM_WP` floats, causing sporadic EEPROM identification errors during Raspberry Pi OS boot.
3. **R35 (4.7kΩ 0402, LCSC C25900):**
   - **Net Connections:** Pad 1 connects to `/PWR_3V3`, Pad 2 connects to `/SCL0`.
   - **Circuit Function:** Primary pull-up resistor for the CM5 I2C clock line (`SCL0`), which communicates with the camera module and camera ID EEPROM. (Note: R36 is the redundant pull-up on SDA0, correctly marked DNP).
   - **Consequence of Omission:** Without R35, the `SCL0` line has NO 3.3V pull-up! The I2C clock line remains permanently low or floats, completely disabling camera communication, probe, and initialization.

### 3.2 Legitimate DNP (Do Not Populate) Components
Six components are marked `(dnp yes)` in the schematic and are appropriately excluded from the manufacturing BOM:

| Reference | Value | Footprint | LCSC Part # | Circuit Role / Rationale for DNP |
|:---|:---|:---|:---|:---|
| **C19** | 0.1uF | C_0402_1005Metric | C1525 | Optional high-frequency bypass capacitor on the camera power tree. |
| **R31** | 0R | R_0402_1005Metric | C17168 | CM5 WiFi_EN option link (leave open for default onboard state). |
| **R32** | 0R | R_0402_1005Metric | C17168 | CM5 BT_EN option link (leave open for default onboard state). |
| **R33** | 0R | R_0402_1005Metric | C17168 | USB0_ID option link. |
| **R36** | 4.7k | R_0402_1005Metric | C25900 | Redundant I2C SDA0 pull-up (already pulled up elsewhere). |
| **Type_C1** | USB_C_16P | USB_C_GCT_USB4105-xx-A | C3020560 | Programming Type-C receptacle (marked DNP; out of stock at JLCPCB). |

---

## 4. Footprint Library (`CM5.pretty`) Syntax & Structural Defects

A comprehensive syntax and paren-balance audit was conducted across all 63 `.kicad_mod` files in `./CM5.pretty/`. Two severe syntax defects were discovered:

### 4.1 `CM5.pretty/Camera_Module_IMX219-D160.kicad_mod` (HTML Comment Injection)
- **Defect:** Seven XML/HTML-style comment tags (`<!-- ... -->`) are embedded directly in the KiCad S-expression file:
  - **Line 42:** `<!-- Silkscreen: Camera base 11.4x11.4mm centered at X=-10.5, Y=0 -->`
  - **Line 49:** `<!-- Camera corner "3" marking -->`
  - **Line 52:** `<!-- Flex Ribbon Neck Silkscreen matching p2_cam_full.png -->`
  - **Line 56:** `<!-- Connector stiffener silkscreen outline -->`
  - **Line 63:** `<!-- Pin 1 Marker Dot at top-right of connector -->`
  - **Line 66:** `<!-- Fabrication Layer: Camera body, lens circles, flex, stiffener -->`
  - **Line 73:** `<!-- Courtyard: 0.25mm boundary around full assembly -->`
- **Parser Impact:** KiCad S-expression syntax specifications forbid HTML comments. KiCad's sexpr tokenizer expects tokens enclosed in parentheses or standard `#` comments. When `kicad-cli` or third-party S-expression parsers encounter `<`, lexer tokenization fails with unexpected token errors (`Got: None` or unexpected `<`).
- **Remediation:** Remove the 7 HTML comment lines from `CM5.pretty/Camera_Module_IMX219-D160.kicad_mod`.

### 4.2 `CM5.pretty/Molex_200528-0150_1x15-1MP_P1.00mm_Horizontal.kicad_mod` (Duplicate Parens & Broken Model Block)
- **Defect:** Truncated / duplicate 3D model definition fragment with unbalanced closing parentheses at lines 501–510:
  ```kicad_mod
  500: 		)
  501: 	)
  502: 		)
  503: 		(scale
  504: 			(xyz 1 1 1)
  505: 		)
  506: 		(rotate
  507: 			(xyz 0 0 0)
  508: 		)
  509: 	)
  510: )
  ```
- **Structural Impact:**
  - Line 501 closes the `(model ...)` S-expression block.
  - Line 502 prematurely closes the entire `(footprint ...)` definition!
  - Lines 503–509 are an orphaned duplicate fragment of `scale` and `rotate` hanging outside any valid block.
  - Line 510 provides an additional orphan closing parenthesis `)`.
  - Net Paren Balance: **-2 (underflow)**. Any strict S-expression parser throws an immediate unclosed/unexpected paren exception.
- **Remediation:** Remove lines 502 to 509 and the extra closing paren at line 510, ending the file cleanly at line 501 with the final footprint closing paren `)`.
