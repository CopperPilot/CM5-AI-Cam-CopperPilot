# Comprehensive BOM, Sourcing, Pinout, and DFM Verification Report
**Project:** CM5 AI Camera Carrier Board (`CM5-AI-Cam-CopperPilot`)  
**Target Assembler:** JLCPCB PCBA  
**Artifacts Audited:**
- Schematic: `CM5-AI-Cam-CopperPilot.kicad_sch` (KiCad 10)
- PCB: `CM5-AI-Cam-CopperPilot.kicad_pcb` (KiCad 10)
- BOM: `jlcpcb_production/assembly/bom_jlcpcb.csv`
- CPL: `jlcpcb_production/assembly/cpl_jlcpcb.csv`
- DRC Signoff: `jlcpcb_production/reports/drc_signoff.rpt`
- ERC Signoff: `jlcpcb_production/reports/erc_signoff.rpt`

---

## 1. Executive Summary & Critical Verdict

A comprehensive cross-domain verification was performed across all 90 schematic/PCB components, the 81-line JLCPCB assembly BOM, LCSC catalog numbers, footprint pad geometries, and PCB routing.

### Verdict: REJECTED FOR PRODUCTION / SHOWSTOPPERS PRESENT
The board in its current state **CANNOT be manufactured or assembled successfully by JLCPCB** due to:
1. **Three Fatal Package Mismatches:**
   - **U5 (MP1658GTF-Z):** Component exists only in SOT-563 (0.5 mm pitch), but PCB footprint is TSOT-23-6 (0.95 mm pitch). Cannot be placed or soldered.
   - **Q1, Q2 (DMG1012T):** Component is SOT-523 (1.0 mm pitch, 1.6 mm body), but PCB footprint is Texas_DRT-3 (0.7 mm pitch, 1.0 x 0.8 mm body). Transistor is ~1.6x larger than the pads.
   - **J2 (USB-A Vertical):** BOM assigns C720523 (XUNPU USB-226-BRY, a Right-Angle connector), but PCB footprint is MOLEX 67298-4090 / 105057-0001 (Vertical through-hole). Pin and shield layouts do not match.
2. **Three Critical Active BOM Omissions:**
   - Resistors **R1** (0R), **R29** (0R), and **R35** (4.7k) are active circuit elements (`dnp no`, `in_bom yes`), but were completely omitted from `bom_jlcpcb.csv`! If assembled, R35 (I2C pullup) will be missing, and control lines for SD VDD and EEPROM write protect will float.
3. **Module1 CPL & BOM Defect (CM5 Connector):**
   - The Raspberry Pi Compute Module 5 requires **two 100-pin Hirose DF40 connectors** (2x C597931). The BOM only lists Quantity 1 for `Module1`, and `cpl_jlcpcb.csv` provides only a single centroid placed directly in the dead zone between the two connector locations.
4. **Thirteen Fatal Open-Circuit Nets in Layout (DRC Failures):**
   - Camera digital core 1.2V power is completely disconnected from J1 Pad 4.
   - Camera CSI differential lane 0 negative line is broken between L1 Pad 3 and J1 Pad 23.
   - USB switch U6 (FSUSB42) Pad 9 (VCC) is disconnected from the 3.3V rail.
   - LDO U2 (1.8V) input and bypass capacitors are disconnected from 3.3V.
   - Buck converter U5 has broken traces on bootstrap (BST) and switch (SW) nodes.

---

## 2. BOM & LCSC Part Number Verification (All 90 Components)

The design contains exactly **90 unique physical component instances** on the PCB:
- **81 components** are listed in `bom_jlcpcb.csv` across 42 BOM lines.
- **3 components (R1, R29, R35)** are active circuit elements (`dnp no`, `in_bom yes`), but were **omitted from `bom_jlcpcb.csv`**.
- **6 components (C19, R31, R32, R33, R36, Type_C1)** are marked `dnp yes` in the schematic and PCB.

### Full Component Audit Table (90 Components)

| Ref Des | Schematic Value | Assigned Footprint | LCSC Part # | JLCPCB Type | Sourcing Status / Description | Verification Result |
|:---|:---|:---|:---|:---|:---|:---|
| **C1, C12, C5** | 2.2uF | C_0402_1005Metric | C23733 | Extended | 2.2uF 10V X5R 0402 Ceramic Cap | **VERIFIED MATCH** |
| **C10, C14, C3** | 100nF | C_0402_1005Metric | C1525 | Basic | 100nF (0.1uF) 50V X7R 0402 | **VERIFIED MATCH** |
| **C11, C22, C4** | 10uF | C_0805_2012Metric | C15850 | Basic | 10uF 25V X5R 0805 Ceramic Cap | **VERIFIED MATCH** |
| **C15, C16, C2, C21, C29, C30, C6, C7, C8, C9** | 1uF | C_0402_1005Metric | C52923 | Basic | 1uF 16V X5R 0402 Ceramic Cap | **VERIFIED MATCH** |
| **C17, C18, C23, C24, C27, C28, C31, C32** | 0.1uF | C_0402_1005Metric | C1525 | Basic | 100nF (0.1uF) 50V X7R 0402 | **VERIFIED MATCH** |
| **C19** | 0.1uF | C_0402_1005Metric | C1525 | Basic | DNP in SCH & PCB; omitted from BOM | **VERIFIED DNP** |
| **C20** | 10pF | C_0402_1005Metric | C32949 | Extended | 10pF 50V C0G/NP0 0402 | **VERIFIED MATCH** |
| **C25, C26** | 22uF | C_0805_2012Metric | C45783 | Extended | 22uF 10V X5R 0805 Ceramic Cap | **VERIFIED MATCH** |
| **DSI1** | DSI_15P | Molex_200528-0150_1x15-1MP_P1.00mm_Horizontal | C2914074 | Extended | Molex 200528-0150 15P 1.0mm FPC | **VERIFIED MATCH** |
| **FB1** | 120R | R_0603_1608Metric | C50843 | Extended | Ferrite Bead 120 Ohm @ 100MHz 0603 | **VERIFIED MATCH** |
| **H3, H4, H5** | Conn_01x03 | PinHeader_1x03_P2.54mm_Vertical | C49257 | Extended | 1x3 Pin Header 2.54mm TH | **VERIFIED MATCH** (Through-Hole assembly required) |
| **HDMI1** | HDMI_Mini_C | HDMI_Mini-C_Molex_47151-0001 | C2013978 | Obsolete/Unverified | Molex 47151-0001 Mini HDMI Type C | **SOURCING RISK** (Part obsolete; no JLCPCB stock) |
| **J1** | IMX219_30P | Camera_Module_IMX219-D160 | C6539772 | Extended | Hirose DF37NB-30DS-0.4V(75) 30P Mezzanine | **VERIFIED MATCH** (Waveshare IMX219 DF37, NOT FH12) |
| **J2** | USB_A_Vertical | MOLEX_USB_67298-4090 | C720523 | Extended | XUNPU USB-226-BRY (Right-Angle TH) | **FATAL MISMATCH** (Footprint is Vertical 105057-0001) |
| **Key1** | SW_Push_SPST | SW_SPST_PTS645Sx43SMTR92 | C318884 | Extended | Tactile Switch SMD 6x6mm | **VERIFIED MATCH** |
| **L1, L2, L3** | MCF1210BF2-900T01 | L_CommonModeChoke_Coilank_ACM1210 | C49073870 | Extended | Coilank ACM1210T900W2 (90 Ohm @ 100MHz) | **VERIFIED MATCH** (Winding 1-2, 4-3) |
| **L5** | LED Red | LED_0603_1608Metric | C2286 | Basic | Red LED 0603 SMD | **VERIFIED MATCH** |
| **L6** | LED Green | LED_0603_1608Metric | C72043 | Basic | Green LED 0603 SMD | **VERIFIED MATCH** |
| **L7** | 4.7uH | L_Bourns_SRP5030CC | C840574 | Extended | Shielded Inductor 4.7uH 5x5mm SMD | **VERIFIED MATCH** |
| **Module1** | ComputeModule5-CM5 | Raspberry-Pi-5-Compute-Module | C597931 | Extended | Hirose DF40C-100DS-0.4V(51) Mezzanine | **FATAL CPL/BOM DEFECT** (Needs 2x C597931 & 2 centroids) |
| **PI1** | Raspberry_Pi_40Pin_GPIO | PinHeader_2x20_P2.54mm_Vertical | C50980 | Extended | 2x20 Pin Header 2.54mm TH | **VERIFIED MATCH** (Through-Hole assembly required) |
| **Q1, Q2** | DMG1012T | Texas_DRT-3 | C20512 | Basic | Diodes Inc DMG1012T-7 (SOT-523) | **FATAL MISMATCH** (Footprint is TI DRT-3 1.0x0.8mm) |
| **R1** | 0R | R_0402_1005Metric | C17168 | Basic | SD_VDD Override pulldown (0R 0402) | **CRITICAL OMISSION FROM BOM** (`dnp no`, not in BOM) |
| **R10** | 22R | R_0402_1005Metric | C25092 | Extended | 22 Ohm 1% 0402 Resistor | **VERIFIED MATCH** |
| **R11, R14, R30, R34** | 10k | R_0402_1005Metric | C25744 | Basic | 10k Ohm 1% 0402 Resistor | **VERIFIED MATCH** |
| **R12, R13** | 1k | R_0402_1005Metric | C11702 | Basic | 1k Ohm 1% 0402 Resistor | **VERIFIED MATCH** |
| **R15, R19** | 100k | R_0402_1005Metric | C25741 | Basic | 100k Ohm 1% 0402 Resistor | **VERIFIED MATCH** |
| **R16** | 10R | R_0402_1005Metric | C25077 | Extended | 10 Ohm 1% 0402 Resistor | **VERIFIED MATCH** |
| **R17, R22, R24** | 0R | R_0402_1005Metric | C17168 | Basic | 0 Ohm 0402 Jumper Resistor | **VERIFIED MATCH** |
| **R2, R3** | 5.1k | R_0402_1005Metric | C25905 | Basic | 5.1k Ohm 1% 0402 Resistor (Type-C CC) | **VERIFIED MATCH** |
| **R20** | 61.9k | R_0402_1005Metric | C25916 | Extended | 61.9k Ohm 1% 0402 Resistor (MP1658 FB) | **VERIFIED MATCH** |
| **R21** | 20k | R_0402_1005Metric | C25765 | Extended | 20k Ohm 1% 0402 Resistor (MP1658 FB) | **VERIFIED MATCH** |
| **R28** | 47k | R_0402_1005Metric | C25792 | Extended | 47k Ohm 1% 0402 Resistor | **VERIFIED MATCH** |
| **R29** | 0R | R_0402_1005Metric | C17168 | Basic | EEPROM Write Protect pulldown | **CRITICAL OMISSION FROM BOM** (`dnp no`, not in BOM) |
| **R31, R32, R33** | 0R | R_0402_1005Metric | C17168 | Basic | DNP in SCH & PCB; omitted from BOM | **VERIFIED DNP** (WiFi_EN, BT_EN, USB0_ID) |
| **R35** | 4.7k | R_0402_1005Metric | C25900 | Basic | SCL0 3.3V Pullup Resistor | **CRITICAL OMISSION FROM BOM** (`dnp no`, not in BOM) |
| **R36** | 4.7k | R_0402_1005Metric | C25900 | Basic | DNP in SCH & PCB; omitted from BOM | **VERIFIED DNP** (SDA0 redundant pullup) |
| **R4, R7** | 4.7k | R_0402_1005Metric | C25900 | Basic | 4.7k Ohm 1% 0402 Resistor | **VERIFIED MATCH** |
| **R5, R8** | 2.2k | R_0402_1005Metric | C25879 | Basic | 2.2k Ohm 1% 0402 Resistor | **VERIFIED MATCH** |
| **TF1** | Micro_SD_Card_Det | SDCARD_MOLEX_503398-1892 | C91145 | Extended | Korean Hroparts TF-01A (Push-Push SMD) | **VERIFIED MATCH** (Designator is TF1, not SD1) |
| **Type_C1** | USB_C_Receptacle_16P | USB_C_GCT_USB4105-xx-A | C3020560 | Extended / Out of Stock | GCT USB4105-GF-A 16P USB 2.0 Type-C | **SOURCING RISK & DNP** (Marked DNP; out of stock) |
| **U1** | RT9193-28GB | SOT-23-5 | C114059 | Extended | Richtek 2.8V 300mA LDO | **VERIFIED MATCH** |
| **U2** | RT9193-18GB | SOT-23-5 | C27416 | Extended | Richtek 1.8V 300mA LDO | **VERIFIED MATCH** |
| **U3** | RT9013-12 | SOT-23-5 | C7434207 | Extended | Richtek 1.2V 500mA LDO | **VERIFIED MATCH** |
| **U4, U7** | DIO7003HCST5 | SOT-23-5 | C157437 | Extended | ST STMPS2171STR (BOM comment mismatch) | **FUNCTIONALLY COMPATIBLE** (Align BOM comment) |
| **U5** | MP1658GTF-Z | TSOT-23-6 | C9900009837 | Special JLCPCB | MPS MP1658GTF-Z (SOT-563, 0.5mm pitch) | **FATAL MISMATCH** (Footprint is TSOT-23-6 0.95mm) |
| **U6** | FSUSB42MX | UQFN-10_1.4x1.8mm_P0.4mm | C11145 | Extended | onsemi FSUSB42UMX (UMLP-10 0.4mm pitch) | **VERIFIED MATCH** (Pad 9 VCC unrouted on PCB!) |
| **U8** | STMPS2171STR | SOT-23-5 | C157437 | Extended | ST STMPS2171STR (SOT-23-5 1A Power Switch) | **VERIFIED MATCH** |
| **X1** | OSC_24MHz | Crystal_SMD_3225-4Pin_3.2x2.5mm | C717686 | Extended | 24MHz SMD 3225 4-pad Crystal | **VERIFIED MATCH** |

---

## 3. Deep-Dive Pinout & Footprint Parity for Critical ICs & Connectors

### 3.1 U5: MP1658GTF-Z (Buck Converter)
- **Manufacturer & MPN:** Monolithic Power Systems (MPS) `MP1658GTF-Z`.
- **Datasheet Package:** **SOT-563** (6-lead, body 1.6 x 1.2 mm, pin pitch 0.50 mm).
- **Datasheet Pinout:**
  - Pin 1: `VIN` (Power Input 4.5V–16V)
  - Pin 2: `SW` (Switching Node)
  - Pin 3: `GND` (Ground)
  - Pin 4: `BST` (Bootstrap Capacitor)
  - Pin 5: `EN` (Enable Input)
  - Pin 6: `FB` (Feedback Voltage Sense, 0.6V reference)
- **Schematic Symbol (`CM5:MP1658GTF-Z`):** Matches pinout (1=VIN, 2=SW, 3=GND, 4=BST, 5=EN, 6=FB).
- **PCB Footprint (`CM5:TSOT-23-6`):**
  - Footprint body: 2.90 x 2.80 mm.
  - Pin pitch: **0.95 mm** (vs 0.50 mm required).
  - Pad width span: **2.275 mm center-to-center** (vs 1.60 mm required).
  - Pad size: 1.325 x 0.60 mm (vs 0.30 x 0.50 mm required).
- **Finding:** **TOTAL PHYSICAL PACKAGE INCOMPATIBILITY**. An SOT-563 IC cannot be placed or soldered onto TSOT-23-6 pads. Furthermore, PCB tracks for `SW` and `BST` have dangling unrouted segments in DRC (`CM5-AI-Cam-CopperPilot-drc.rpt`).

### 3.2 U6: FSUSB42UMX (USB 2.0 High-Speed Switch)
- **Manufacturer & MPN:** onsemi `FSUSB42UMX` (LCSC `C11145`).
- **Datasheet Package:** 10-lead UMLP / UQFN (1.4 x 1.8 mm, 0.40 mm pitch).
- **Datasheet & Footprint Pinout:**
  - Pin 1: `D+` (Common USB D+) -> PCB Net `/USB0_B_P`
  - Pin 2: `D-` (Common USB D-) -> PCB Net `/USB0_B_N`
  - Pin 3: `GND` -> PCB Net `GND`
  - Pin 4: `HSD1-` (Port 1 D-) -> PCB Net `/USBB_N`
  - Pin 5: `HSD1+` (Port 1 D+) -> PCB Net `/USBB_P`
  - Pin 6: `HSD2-` (Port 2 D-) -> PCB Net `/USBD0_N`
  - Pin 7: `HSD2+` (Port 2 D+) -> PCB Net `/USBD0_P`
  - Pin 8: `/OE` (Active Low Enable) -> PCB Net `GND` (Permanently enabled)
  - Pin 9: `VCC` (Supply 3.0V–4.4V) -> PCB Net `/CM5_3V3`
  - Pin 10: `SEL` (Select) -> PCB Net `/USB_SEL`
- **Finding:** Symbol, footprint, and pinout are electrically and geometrically matched.
- **Critical Flaw:** **Pad 9 (/CM5_3V3) is UNCONNECTED on the PCB** (`drc_signoff.rpt`). The 3.3V via is unrouted to pad 9. U6 has zero power supply; USB switching is completely non-functional.

### 3.3 U4, U7, U8: STMPS2171STR / DIO7003HCST5 (Power Distribution Switches)
- **Device Family:** 1A high-side power distribution switches with active-high enable and overcurrent flag.
- **Package:** SOT-23-5L (JEDEC MO-178 AA).
- **Pinout:**
  - Pin 1: `OUT` (Power Switch Output)
  - Pin 2: `GND` (Ground)
  - Pin 3: `FAULT` (Open-Drain Fault Flag)
  - Pin 4: `EN` (Active-High Enable)
  - Pin 5: `IN` (Power Supply Input)
- **Schematic & PCB Connections:**
  - `U4` (HDMI 5V switch): Pin 1=`/HDMI_5V`, Pin 2=`GND`, Pin 3=NC, Pin 4=`/HDMI_5V_EN`, Pin 5=`/CM5_5V`.
  - `U7` (SD 3.3V switch): Pin 1=`/SD_3.3V`, Pin 2=`GND`, Pin 3=NC, Pin 4=`/SD_PWREN`, Pin 5=`/PWR_3V3`.
  - `U8` (USB 5V switch): Pin 1=`/USB_5V`, Pin 2=`GND`, Pin 3=`/USB_FAULT`, Pin 4=`/CM5_5V` (tied HIGH), Pin 5=`/CM5_5V`.
- **Finding:** Pinout and footprints are verified. In the BOM, U4 and U7 are designated `DIO7003HCST5` while U8 is designated `STMPS2171STR`, but all three use LCSC `C157437` (`STMPS2171STR`). They are 100% pin- and spec-compatible; BOM comments should be unified to prevent factory audit pauses.

### 3.4 L1, L2, L3: Common Mode Chokes (MCF1210BF2-900T01 / ACM1210)
- **Footprint:** `CM5:L_CommonModeChoke_Coilank_ACM1210` (1.20 x 1.00 mm).
- **Winding Configuration:**
  - Winding A: Between Pad 1 (-0.51, -0.32) and Pad 2 (-0.51, +0.32) -> Differential P line.
  - Winding B: Between Pad 4 (+0.51, -0.32) and Pad 3 (+0.51, +0.32) -> Differential N line.
- **PCB Connections:**
  - `L1`: Pad 1=`/CAM0_D0_P`, Pad 2=`/CSI_D0_P`, Pad 4=`/CAM0_D0_N`, Pad 3=`/CSI_D0_N`.
  - `L2`: Pad 1=`/CAM0_D1_P`, Pad 2=`/CSI_D1_P`, Pad 4=`/CAM0_D1_N`, Pad 3=`/CSI_D1_N`.
  - `L3`: Pad 1=`/CAM0_CLK_P`, Pad 2=`/CSI_CLK_P`, Pad 4=`/CAM0_CLK_N`, Pad 3=`/CSI_CLK_N`.
- **Finding:** Winding mapping is correct.
- **Critical Flaw:** **Pad 3 (/CSI_D0_N) of L1 is UNCONNECTED to J1 Pad 23** (`drc_signoff.rpt`). Camera CSI data lane 0 negative line is broken.

### 3.5 J1: IMX219 30-pin Camera Connector
- **Footprint in PCB:** `CM5:Camera_Module_IMX219-D160`.
- **Actual Hardware:** **Hirose DF37NB-30DS-0.4V(75)** (LCSC `C6539772`), dual-row 30-pin 0.40 mm pitch mezzanine connector for Waveshare IMX219-D160 module.
- **Correction vs Prompt:** Prompt asked about Hirose FH12-30S (0.5 mm single-row FPC). The design uses the DF37NB-30DS-0.4V mezzanine connector directly mating with the sensor module.
- **Pinout Verification:**
  - Pins 1-2: NC
  - Pin 3: `/1V8` (Analogue 1.8V)
  - Pin 4: `/1V2` (Digital core 1.2V) -> **UNCONNECTED ON PCB (DRC ERROR)**
  - Pin 5: `/CAM_GPIO` (Powerdown)
  - Pins 6, 8, 9, 12, 15, 16, 19, 22, 25, 28: `GND`
  - Pin 7: `/MCLK` (24 MHz Master Clock)
  - Pin 10: `/2V8` (Analogue 2.8V)
  - Pins 20-21: CSI Data Lane 1 (`/CSI_D1_N`, `/CSI_D1_P`)
  - Pins 23-24: CSI Data Lane 0 (`/CSI_D0_N`, `/CSI_D0_P`) -> **PIN 23 UNCONNECTED ON PCB (DRC ERROR)**
  - Pins 26-27: CSI Clock Lane (`/CSI_CLK_N`, `/CSI_CLK_P`)
  - Pins 29-30: I2C Interface (`/SCL_1V8`, `/SDA_1V8`)
- **Finding:** Pinout is correct for IMX219 DF37. Two fatal unrouted nets on PCB: Pin 4 (1.2V core power disconnected) and Pin 23 (CSI D0_N disconnected).

### 3.6 Type_C1: USB4105-GF-A (16-Pin USB 2.0 Type-C Receptacle)
- **Manufacturer & MPN:** Global Connector Technology (GCT) `USB4105-GF-A` (LCSC `C3020560`).
- **Footprint:** `CM5:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`.
- **Pinout:**
  - A1/B12, A12/B1: `GND`
  - A4/B9, A9/B4: `/CM5_5V` (VBUS input)
  - A5: `/CC1` (pulled down by R2 5.1k)
  - B5: `/CC2` (pulled down by R3 5.1k)
  - A6/B6: `/USBB_P` (USB 2.0 D+)
  - A7/B7: `/USBB_N` (USB 2.0 D-)
  - A8/B8: NC (SBU1/SBU2)
  - Shell S1: `GND`
- **Finding:** Footprint and schematic pinout are correct.
- **Issues:**
  1. Marked `dnp yes` in schematic and PCB; omitted from BOM. The board will be assembled without a USB-C connector!
  2. Currently listed as out of stock on LCSC.
  3. Pad B4 has an unrouted airwire to `/CM5_5V` on the PCB (`drc_signoff.rpt`).

### 3.7 J2: Vertical USB-A Receptacle
- **Footprint:** `CM5:MOLEX_USB_67298-4090` (Vertical through-hole, based on Molex `105057-0001`).
- **Assigned BOM Part:** `C720523` -> **XUNPU USB-226-BRY**.
- **Finding:** **FATAL MISMATCH**. XUNPU USB-226-BRY is a **right-angle** through-hole receptacle. The PCB footprint is a **vertical/straight** through-hole receptacle. Leads and shield legs will not fit. Requires replacement with vertical through-hole USB-A (e.g. C698207) or through-hole manual assembly.

### 3.8 HDMI1: Mini HDMI Type C Receptacle
- **Footprint:** `CM5:HDMI_Mini-C_Molex_47151-0001` (SMD signal pads + 4 TH shield tabs).
- **Assigned BOM Part:** `C2013978`.
- **Pinout Verification:** Conforms strictly to HDMI 1.4/2.0 Type-C Mini specification (Pads 1-19: TMDS Clock/Data differential pairs interleaved with shields, CEC, DDC I2C, +5V, HPD).
- **Sourcing Risk:** Molex 47151-0001 is obsolete. `C2013978` has no stock at JLCPCB.

### 3.9 SD1 / TF1: MicroSD Socket
- **Designator:** `TF1` in schematic, PCB, and BOM (prompt referred to SD1).
- **Assigned BOM Part:** `C91145` -> Korean Hroparts `TF-01A` (Push-Push SMD).
- **Footprint:** `CM5:SDCARD_MOLEX_503398-1892`.
- **Pinout:** Standard 8-pin MicroSD + Card Detect + GND tabs. Signal assignment verified.

### 3.10 Q1, Q2: DMG1012T (I2C Level Shifter MOSFETs)
- **Assigned BOM Part:** `C20512` -> Diodes Inc `DMG1012T-7` in **SOT-523** package (1.6 x 1.6 mm, 1.0 mm lead pitch).
- **PCB Footprint:** `CM5:Texas_DRT-3` (TI DRT-3 package, 1.0 x 0.8 mm, 0.70 mm pitch, 0.3 x 0.3 mm pads).
- **Finding:** **FATAL PACKAGE MISMATCH**. The physical SOT-523 transistor is ~1.6x larger than the DRT-3 pad pattern. It cannot be soldered.
- **PCB Defect:** Pad 2 of Q2 (/SDA_1V8) is unrouted to R8 (`drc_signoff.rpt`).
- **Resolution:** Change footprint to `CM5:SOT-523` (already present in the project footprint library!).

---

## 4. Package Compatibility & Pad Geometry Analysis

| Component | BOM Package | PCB Footprint | Required Lead Spacing | Actual Footprint Pad Spacing | Assembly Compatibility |
|:---|:---|:---|:---|:---|:---|
| **U5 (MP1658)** | SOT-563 | TSOT-23-6 | 0.50 mm pitch; 1.6 mm span | 0.95 mm pitch; 2.275 mm span | **INCOMPATIBLE** (Will not bridge pads) |
| **Q1, Q2 (DMG1012T)** | SOT-523 | Texas_DRT-3 | 1.00 mm pitch; 1.29 mm span | 0.70 mm pitch; 0.85 mm span | **INCOMPATIBLE** (Pads too small/narrow) |
| **J2 (USB-A)** | Right-Angle TH | MOLEX 67298-4090 (Vertical) | Side-entry right-angle pin array | Vertical straight pin array | **INCOMPATIBLE** (Mechanical pin clash) |
| **Module1 (CM5)** | 2x DF40 (100P) | Raspberry-Pi-5-Compute-Module | Two 100-pin connectors separated by 28 mm | Single monolithic 200-pin footprint | **CPL COLLISION** (Centroid centered in air) |

---

## 5. Prioritized Showstoppers & Actionable Remediation Plan

### Tier 1: Fatal Assembly Showstoppers (Factory Rejection / Assembly Failure)
1. **U5 Footprint Mismatch:** Change U5 footprint from `TSOT-23-6` to `SOT-563` (or substitute an equivalent buck converter available in TSOT-23-6, e.g. MP2143 / SY8089).
2. **Q1, Q2 Footprint Mismatch:** Change Q1 and Q2 footprints from `Texas_DRT-3` to `CM5:SOT-523`.
3. **J2 Footprint/Part Mismatch:** Replace `C720523` with a vertical through-hole USB-A connector part number (e.g. `C698207`) or update footprint to match right-angle connector.
4. **Module1 CPL & BOM Defect:** Split `Module1` into two distinct connector designators (`J1A`, `J1B`) using `CONN_DF40C-100DS-0.4V51_HIR` so that `bom_jlcpcb.csv` has Quantity 2 of `C597931` and `cpl_jlcpcb.csv` has two individual pick-and-place centroids.

### Tier 2: Fatal PCB Open-Circuit / Unrouted Traces (Circuit Inoperability)
1. **Camera 1.2V Power (J1 Pin 4):** Connect `/1V2` track on B.Cu to J1 Pad 4 on F.Cu.
2. **Camera CSI Lane 0 Negative (J1 Pin 23):** Route trace between L1 Pad 3 and J1 Pad 23.
3. **USB Switch Power (U6 Pin 9):** Connect `/CM5_3V3` via to U6 Pad 9.
4. **LDO 1.8V Input (U2 Pin 1, C5, C12):** Connect `/PWR_3V3` rail to U2 Pin 1 and bypass caps.
5. **Buck Converter SW & BST (U5):** Route bootstrap track `/MP1658_BST` and snubber resistor `/MP1658_SW`.
6. **I2C SDA Level Shifter (Q2 Pin 2):** Connect `/SDA_1V8` between Q2 Pad 2 and R8.
7. **USB-C 5V Input (Type_C1 Pad B4):** Route `/CM5_5V` trace to Type_C1 Pad B4.

### Tier 3: Critical BOM Omissions & Configuration Discrepancies
1. **Omitted Resistors:** Add `R1` (0R), `R29` (0R), and `R35` (4.7k) to `bom_jlcpcb.csv`. Without R35, the I2C bus will have no 3.3V pullup; without R1 and R29, SD_VDD and EEPROM_WP control lines will float.
2. **Type_C1 DNP Flag:** If USB-C power/data is required on manufactured boards, remove `dnp yes` from Type_C1, assign an in-stock Type-C connector, and export into BOM and CPL.
3. **BOM Comment Alignment:** Change U4 and U7 comments in BOM from `DIO7003HCST5` to `STMPS2171STR` to match LCSC part `C157437`.
4. **HDMI1 & Type_C1 Sourcing:** Source active drop-in replacements for obsolete Molex 47151-0001 (HDMI) and out-of-stock GCT USB4105-GF-A.
