# Comprehensive Schematic Logical Wiring & Defect Audit: CM5 AI Camera Carrier Board

**Document Path:** `./.copperpilot/notes/comprehensive-schematic-defect-audit.md`  
**Date:** 2026-10-15  
**Target Platform:** Raspberry Pi Compute Module 5 (CM5)  
**Primary Schematic:** `CM5-AI-Cam-CopperPilot.kicad_sch` (KiCad 10.0.3)  
**Project Symbol Library:** `CM5.kicad_sym`  
**Footprint Library:** `CM5.pretty/`  
**Reference Architecture:** Waveshare CM5 Nano Base Board (C) (`nano-base-board-c-sch.pdf`)  
**Audited Datasheets:** Monolithic Power Systems MP1658, onsemi FSUSB42UMX, DIOO DIO7003, STMicroelectronics STMPS2171STR, Sony IMX219, Raspberry Pi CM5 Mezzanine Interface Specification.

---

## 1. Executive Summary

An exhaustive cross-domain engineering audit was performed on `CM5-AI-Cam-CopperPilot.kicad_sch` and its companion library `CM5.kicad_sym`. Every net, pin connection, component rating, and symbol definition was cross-checked against manufacturer component datasheets, the official Raspberry Pi Compute Module 5 design guide, and the Waveshare CM5 Nano Base Board (C) reference design.

The audit revealed **14 critical, fatal, and high-severity design defects**:
1. **Buck Converter Destruction Risk (U5):** C21 (1µF) is wired in series with R16 (10Ω) between the SW switching node and GND. At 600 kHz switching frequency on 5V, this capacitive load dissipates ~15 Watts across a 0402 1/16W resistor, causing immediate resistor burnout and severe switcher damage. Furthermore, U5 is assigned a TSOT-23-6 footprint, whereas the MP1658GTF-Z only exists in an ultra-miniature SOT-563 package.
2. **Total Power Loss on Mini-HDMI & MicroSD (U4, U7):** U4 and U7 are designated `DIO7003HCST5`, but the symbol in `CM5.kicad_sym` uses the pinout of an STMPS2171/TPS2051. Because the physical DIO7003 has Pin 1=EN and Pin 3=OUT (reversed from STMPS2171), physical Pin 1 (chip enable gate) is tied to the load, while physical Pin 3 (switched output) floats. Both the Mini-HDMI 5V rail and MicroSD 3.3V rail receive 0V.
3. **MIPI CSI-2 Differential P-to-N Dead Short (L1, L2, L3):** In common-mode chokes L1, L2, and L3, the physical windings connect Pad 1 to Pad 4, and Pad 2 to Pad 3. The schematic connects `CAM0_D0_P` to Pad 1 and `CAM0_D0_N` to Pad 4. Winding A directly dead-shorts the positive and negative differential lines together. Zero video data reaches the CM5.
4. **I2C Level Shifter Footprint & Biasing Flaws (Q1, Q2):** Q1 and Q2 (`DMG1012T` SOT-523) are assigned a leadless `Texas_DRT-3` footprint (1.0 × 0.8 mm) meant for TVS diodes; transistor leads physically miss the pads. Furthermore, redundant pull-ups R35/R36 to 3.3V in parallel with R4/R7 to `GPIO_VREF` create a cross-rail resistive divider that back-feeds 1.8V to 2.55V when 1.8V GPIO mode is selected.
5. **Camera Standby 3.3V Overvoltage (J1 Pin 5):** CM5 3.3V GPIO `CAM_GPIO` is routed directly to J1 Pin 5 (`/PWDN`), violating the IMX219 1.8V digital I/O maximum input rating.
6. **USB Switching Lockout (U6, H4):** The boot/flashing multiplexer lacks coordinated switching. Jumpering H4 to pull `nRPIBOOT` to GND leaves `USB_SEL` pulled high to 3.3V by R28, locking the USB bus to the host USB-A port and preventing `rpiboot` flashing over Type-C.
7. **Permanent EEPROM Write-Protection (R29):** R29 (0Ω) grounds `EEPROM_nWP` and is marked `dnp no`, permanently write-protecting CM5 firmware.
8. **Disabled USB-PD Fast Charging (Module1 Pins 94 & 96):** CM5 CC lines are unconnected, preventing 5V @ 5A negotiation with official Pi 27W supplies.

---

## 2. Comprehensive Defect Register

| Defect ID | Reference Designators | Subsystem | Severity | Failure Mode & Root Cause | Corrective Action |
|:---|:---|:---|:---|:---|:---|
| **DEF-01** | `U5`, `C21`, `R16` | Power: Buck Converter | **FATAL** | **15W Switch Node Dissipation / Resistor Burnout:** C21 (1µF) and R16 (10Ω) are wired between SW and GND as a snubber. At 600 kHz, 1µF dissipates 15W across a 1/16W 0402 resistor, causing rapid destruction. | Remove C21 and R16 from SW node, or replace with standard high-frequency snubber: 330pF–470pF ceramic in series with 2.2Ω–4.7Ω. Retain C24 (0.1µF) strictly between BST (Pin 4) and SW (Pin 2). |
| **DEF-02** | `U5` | Power: Buck Converter | **CRITICAL** | **Footprint Package Mismatch:** `MP1658GTF-Z` is manufactured only in SOT-563 (1.6 × 1.6 mm, 0.5 mm pitch). Footprint assigned is TSOT-23-6 (2.9 × 2.8 mm, 0.95 mm pitch). IC cannot be soldered. | Change U5 footprint from `CM5:TSOT-23-6` to standard `SOT-563` land pattern matching MPS package drawing. |
| **DEF-03** | `U4`, `U7` | Power: Load Switches | **FATAL** | **Reversed Enable & Output Pins (0V Output):** Symbol uses TPS2051/STMPS2171 pinout (Pin 1=OUT, 3=FAULT, 4=EN). DIO7003 datasheet is Pin 1=EN, 2=GND, 3=OUT, 4=FLG, 5=IN. Output load is wired to EN gate; actual switched OUT floats. | In `CM5.kicad_sym`, redefine `DIO7003HCST5` symbol pins to match datasheet: Pin 1=EN, Pin 3=OUT, Pin 4=FLG. Or replace component MPN with STMPS2171STR across schematic and BOM. |
| **DEF-04** | `L1`, `L2`, `L3` | Camera: MIPI CSI-2 | **FATAL** | **P-to-N Dead Short on Differential Pairs:** Footprint pad numbering (1=TL, 2=BL, 3=BR, 4=TR) and internal choke coils (1 to 4, 2 to 3) cause Winding A to connect Pad 1 (`CAM0_D0_P`) directly to Pad 4 (`CAM0_D0_N`), dead-shorting the pair. | Redefine `MCF1210BF2-900T01` symbol in `CM5.kicad_sym`: Coil 1 between Pin 1 and Pin 4; Coil 2 between Pin 2 and Pin 3. Verify straight-through routing. |
| **DEF-05** | `Q1`, `Q2` | Camera: I2C Level Shifter | **CRITICAL** | **Footprint Package Mismatch:** Transistors are `DMG1012T-7` (SOT-523, 1.6 × 1.6 mm gull-wing). Assigned footprint is `CM5:Texas_DRT-3` (1.0 × 0.8 mm leadless DFN). Pins float off pads. | Change footprint of Q1 and Q2 from `CM5:Texas_DRT-3` to standard `Package_TO_SOT_SMD:SOT-523`. |
| **DEF-06** | `R4`, `R7`, `R35`, `R36` | Camera: I2C Pull-Ups | **HIGH** | **Cross-Rail Voltage Contention:** SCL0/SDA0 have R35/R36 (4.7kΩ to PWR_3V3) in parallel with R4/R7 (4.7kΩ to GPIO_VREF). When H5 selects 1.8V for GPIO_VREF, a 3.3V-to-1.8V divider holds the bus at 2.55V. | Tie R4 and R7 pull-ups strictly to 3.3V bus; mark R35 and R36 as DNP to eliminate parallel contention. |
| **DEF-07** | `J1`, `R17`, `Module1` | Camera: Standby / Reset | **HIGH** | **3.3V Overvoltage on IMX219 /PWDN Pin:** CM5 Pin 97 (`Camera_GPIO`, 3.3V) routes directly to J1 Pin 5 (`/PWDN`). IMX219 digital I/O rail is 1.8V; 3.3V violates absolute maximum input voltage. | Insert a resistive divider (e.g. 10k top, 12k bottom to GND) or level-shift `CAM_GPIO` to 1.8V before driving J1 Pin 5. |
| **DEF-08** | `X1`, `C20` | Camera: MCLK Oscillator | **MEDIUM** | **Improper Oscillator Supply Bypass Value:** C20 is 10pF on the 1.8V supply of active 24MHz CMOS oscillator X1. Provides zero low-impedance decoupling (663Ω reactance at 24MHz). | Change C20 value from 10pF to 0.1µF (100nF) 16V X7R ceramic. |
| **DEF-09** | `U6`, `H4`, `R28` | USB: Multiplexing Logic | **HIGH** | **Flashing Mode Lockout (rpiboot Inaccessible):** U6 SEL is pulled up by R28 to 3.3V. H4 is 1x3 (1:PI_BOOT, 2:GND, 3:USB_SEL). A standard 2-pin shunt cannot pull both PI_BOOT and USB_SEL low simultaneously. | Replicate reference Q3/Q4 dual-FET buffer circuit or use a DPDT switch / 2x2 header to ensure grounding PI_BOOT also grounds USB_SEL. |
| **DEF-10** | `R29` | CM5 Mezzanine: Strapping | **HIGH** | **Permanent EEPROM Write-Protection:** R29 (0Ω) pulls `EEPROM_nWP` to GND and is set to `dnp no` (`in_bom yes`). Bootloader updates and recovery will fail. | Change R29 property to `(dnp yes)` in schematic and omit from production BOM. |
| **DEF-11** | `Module1` (Pins 94, 96) | Power: USB-PD Negotiation | **MEDIUM** | **USB-PD 5V@5A Fast Charging Inoperable:** Module1 Pin 94 (`AnalogIP0`/CC2) and Pin 96 (`AnalogIP1`/CC1) are unconnected. Only static 5.1kΩ pulldowns exist on Type-C. | Route Type_C1 Pin A5 (CC1) to Module1 Pin 96, and Type_C1 Pin B5 (CC2) to Module1 Pin 94 to allow CM5 PMIC USB-PD negotiation. |
| **DEF-12** | `TF1` (Pin 10) | Storage: MicroSD Card | **LOW** | **Floating Card Detect Terminal:** TF1 Pin 10 (`DET_A`) is completely unconnected. Hardware card insertion/removal detection is inactive. | Connect Pin 10 to a CM5 GPIO with pull-up, or document polling-only operation. |
| **DEF-13** | External Ports | System: ESD Protection | **MEDIUM** | **Zero ESD Protection on User Interfaces:** No TVS diodes exist on Type-C, USB-A, Mini-HDMI, or MicroSD card socket. | Add multi-channel low-capacitance TVS diode arrays (e.g. USBLC6-2SC6, TPD4E05U06, ESDALC6V1) to external I/O pins. |
| **DEF-14** | `Module1` | Assembly: SMT Manufacturing | **CRITICAL** | **Unified Footprint & Centroid for Dual Connectors:** CM5 requires two physical 100-pin connectors (2x Hirose DF40). BOM lists Qty 1 and CPL has 1 centroid in the void between connectors. | Split Module1 into two distinct schematic symbols and PCB footprints (`H1A` and `H1B`), each with its own pick-and-place centroid. |

---

## 3. Subsystem Deep-Dive Analysis

### 3.1 Section 1: Power Architecture & Regulators

#### 5V Input Power Path
- **VBUS Ingestion:** Input 5V is supplied via `Type_C1` on VBUS pins A4, A9, B4, B9, merged onto net `/CM5_5V`.
- **Decoupling:** Decoupled by C11 (10µF 25V 0805), C4 (10µF 25V 0805), C17 (0.1µF), C22 (10µF), C23 (0.1µF), and C30 (1µF).
- **Protection Gaps:** No reverse-polarity protection, ideal diode controller, PTC resettable fuse, or overvoltage clamping TVS diode exists on `/CM5_5V`. Any reverse voltage or 12V/20V surge from an improper USB-PD charger will directly destroy the CM5 module and all downstream regulators.
- **USB-PD CC Logic:** CC1 (A5) and CC2 (B5) are pulled down to GND via R3 (5.1kΩ) and R2 (5.1kΩ), establishing standard UFP sink operation (5V up to 3A). Because CM5 Pins 94 and 96 are unconnected, the CM5 cannot perform BMC communication to negotiate 5V @ 5A.

#### Synchronous Buck Converter U5 (MP1658GTF-Z)
- **Topological Purpose:** Steps down 5V (`/CM5_5V`) to 3.3V (`/PWR_3V3`) to power camera LDOs, MicroSD card switch, DSI display logic, pull-ups, and user peripherals.
- **Feedback Network (FB):**
  - Voltage reference: \(V_{\text{FB}} = 0.807\text{ V}\).
  - Schematic values: \(R_{20} = 61.9\text{ k}\Omega\) (top), \(R_{21} = 20\text{ k}\Omega\) (bottom).
  - Regulated output: \(V_{\text{OUT}} = 0.807 \times (1 + 61.9/20) = 3.305\text{ V}\). This correctly targets 3.3V.
- **Enable Circuit (EN):**
  - Pin 5 (`EN`) is pulled up to `/CM5_5V` via R19 (100kΩ). The MP1658 internal 2.8V Zener clamp limits Zener current to \((5\text{V} - 2.8\text{V}) / (100\text{k}\Omega + 35\text{k}\Omega) = 16.3\mu\text{A}\), well below the 100µA maximum rating.
- **Bootstrap / Snubber Wiring Catastrophe (DEF-01):**
  - Pin 4 (`BST`) is connected via C24 (0.1µF) to Pin 2 (`SW`). This forms the required floating bootstrap gate supply.
  - However, R16 (10Ω 0402) is connected from Pin 2 (`SW`) to net `/MP1658_BST_R`, which connects through C21 (1µF 0402) to `GND`.
  - While intended as a switch-node snubber, a **1µF** capacitor at 600 kHz switching frequency has an impedance of only \(X_C = \frac{1}{2\pi \cdot 600\text{kHz} \cdot 1\mu\text{F}} = 0.265\ \Omega\).
  - The power dissipated in R16 is approximately \(P = C \cdot V_{\text{IN}}^2 \cdot f_{\text{SW}} = 1\mu\text{F} \times 25\text{V}^2 \times 600\text{kHz} \approx 15\text{ W}\).
  - The 0402 resistor will burn out instantaneously upon power application, potentially creating an arc or shorting the SW node directly to ground.
- **Package Mismatch (DEF-02):**
  - Footprint `CM5:TSOT-23-6` (2.9 × 2.8 mm, 0.95 mm pitch) is assigned, but `MP1658GTF-Z` is an ultra-miniature SOT-563 (1.6 × 1.6 mm, 0.5 mm pitch).

#### Low-Dropout Regulators (U1, U2, U3: IMX219 Supplies)
- **U1 (2.8V Analog Supply - VA2V8):** `RT9193-28GB` (SOT-23-5). Input is fed from `/PWR_3V3` via ferrite bead FB1 (120Ω @ 100MHz). Dropout at 300mA is ~220mV; headroom from 3.3V is ~500mV. While functional, feeding FB1 from 5V would provide superior PSRR for sensitive analog sensor circuitry.
- **U2 (1.8V Digital I/O Supply - VO1V8):** `RT9193-18GB` (SOT-23-5). Input fed from `/PWR_3V3`. Powers sensor I/O, level shifters Q1/Q2, and oscillator X1.
- **U3 (1.2V Digital Core Supply - VD1V2):** `RT9013-12` (SOT-23-5, 500mA). Input fed from `/PWR_3V3`. Powers IMX219 digital processing core.
- **Sequencing & Enable:** All three LDOs have Pin 3 (`EN`) tied to `/CAM_GPIO'`, controlled by CM5 Pin 97 with 100kΩ pulldown R15. When CM5 drives `Camera_GPIO` high, all three rails power up concurrently.

#### Power Switches (U4, U7, U8)
- **U4 (HDMI 5V Switch):** Labeled `DIO7003HCST5`. Reversing Pin 1 (EN) and Pin 3 (OUT) prevents power delivery to Mini-HDMI Pin 18 (0V output).
- **U7 (MicroSD 3.3V Switch):** Labeled `DIO7003HCST5`. Reversing Pin 1 and Pin 3 prevents power delivery to MicroSD Pin 4 (0V output).
- **U8 (USB-A 5V Switch):** `STMPS2171STR` (SOT-23-5). Pinout matches STMPS2171. Pin 4 (`EN`) is tied directly to `/CM5_5V` (always active; no host power-cycling capability). Pin 3 (`FAULT`) connects to `/USB_FAULT` with R34 pull-up, but is unrouted to CM5.

---

### 3.2 Section 2: USB Switching & Type-C / Type-A Logic

#### Multiplexer Architecture (U6: FSUSB42UMX)
- **Component:** onsemi FSUSB42UMX high-speed USB 2.0 dual DPDT switch in 10-lead UMLP (1.4 × 1.8 mm, 0.4 mm pitch).
- **Datasheet Pinout Verification:**
  - Pin 1: D+ (Common) -> Net `/USB0_B_P` (via R24 0R to CM5 Pin 105 `USB2_P`)
  - Pin 2: D- (Common) -> Net `/USB0_B_N` (via R22 0R to CM5 Pin 103 `USB2_N`)
  - Pin 3: GND -> Net `GND`
  - Pin 4: HSD1- (Port 1) -> Net `/USBB_N` (to Type_C1 Pins A7/B7 D-)
  - Pin 5: HSD1+ (Port 1) -> Net `/USBB_P` (to Type_C1 Pins A6/B6 D+)
  - Pin 6: HSD2- (Port 2) -> Net `/USBD0_N` (to USB-A J2 Pin 2 D-)
  - Pin 7: HSD2+ (Port 2) -> Net `/USBD0_P` (to USB-A J2 Pin 3 D+)
  - Pin 8: /OE -> Net `GND` (Active low enable; permanently grounded = enabled)
  - Pin 9: VCC -> Net `/CM5_3V3` (Power supply)
  - Pin 10: SEL -> Net `/USB_SEL` (Path select)
- **Polarity & Pinout Truth:** Contrary to earlier assumptions in preliminary defect registers, the symbol definition in `CM5.kicad_sym` accurately matches the official onsemi `fsusb42-d.pdf` datasheet for the 10-lead UMLP package. Pin 8 is `/OE`, Pin 9 is `VCC`, Pin 6 is `HSD2-`, and Pin 7 is `HSD2+`. Differential polarity to both Type-C and USB-A is structurally correct in the schematic.

#### Selection & Boot Strapping Logic (DEF-09)
- **Truth Table:**
  - `SEL = 0` (LOW): D± routes to HSD1± (`Type_C1` programming port)
  - `SEL = 1` (HIGH): D± routes to HSD2± (`J2` USB-A Host port)
- **Circuit Failure:**
  - Net `/USB_SEL` is pulled up to 3.3V via R28 (47kΩ).
  - Header H4 is a standard 1x3 0.1" header: Pin 1 = `/PI_BOOT`, Pin 2 = `GND`, Pin 3 = `/USB_SEL`.
  - When no jumper is installed, the board is in normal boot mode, and U6 routes USB to the USB-A host port.
  - To flash the CM5 via `rpiboot`, `/PI_BOOT` (`nRPIBOOT`) must be pulled to GND, AND `/USB_SEL` must be pulled to GND.
  - A standard 2-pin shunt across H4 Pins 1-2 pulls `nRPIBOOT` low, but leaves `USB_SEL` high (USB-A Host). The host PC connected to Type-C cannot see the CM5.
  - A shunt across H4 Pins 2-3 pulls `USB_SEL` low (Type-C), but leaves `nRPIBOOT` floating (normal boot).
  - The board cannot be placed into eMMC flashing mode without fabricating a custom 3-pin shorting bridge across all three pins of H4.

---

### 3.3 Section 3: Camera (CSI / I2C / Power) Interface & Level Shifters

#### MIPI CSI-2 Differential Pair Short Circuit (DEF-04)
- **Choke Internal Geometry:** SMD common-mode filters (`Coilank ACM1210` / `MCF1210BF2-900T01`) have two straight-through coils:
  - Coil A connects Pad 1 (Top-Left) to Pad 4 (Top-Right).
  - Coil B connects Pad 2 (Bottom-Left) to Pad 3 (Bottom-Right).
- **Schematic Connections on L1, L2, L3:**
  - L1 Pad 1 (`CAM0_D0_P`) and Pad 4 (`CAM0_D0_N`) are connected to Coil A.
  - L1 Pad 2 (`CSI_D0_P`) and Pad 3 (`CSI_D0_N`) are connected to Coil B.
- **Physical Result:**
  - Coil A internally bridges `CAM0_D0_P` directly to `CAM0_D0_N` with ~0.5Ω DCR.
  - Coil B internally bridges `CSI_D0_P` directly to `CSI_D0_N` with ~0.5Ω DCR.
  - Identical differential shorts exist on L2 (Lane 1) and L3 (Clock).
  - High-speed differential signaling is completely suppressed.

#### I2C Level Shifter & Pull-Up Network (DEF-05 & DEF-06)
- **MOSFET Level Shifter:** Q1 and Q2 (`DMG1012T`) translate between CM5 3.3V I2C (`SCL0`/`SDA0`) and IMX219 1.8V I2C (`SCL_1V8`/`SDA_1V8`). Gates are biased to 1.8V (`VO1V8`).
- **Footprint Error:** Q1/Q2 are assigned `CM5:Texas_DRT-3` (1.0 × 0.8 mm DFN), while DMG1012T is a 3-lead SOT-523 (1.6 × 1.6 mm). Transistor leads cannot solder to the pads.
- **Pull-Up Resistor Contention:**
  - 1.8V domain has R5 (2.2kΩ) and R8 (2.2kΩ) to `/1V8`.
  - 3.3V domain has R4 (4.7kΩ) and R7 (4.7kΩ) tied to `/GPIO_VREF`, AND R35 (4.7kΩ) and R36 (4.7kΩ) tied to `/PWR_3V3`.
  - Both R35 and R36 are active (`dnp no`, `in_bom yes`) in the schematic.
  - If H5 sets `GPIO_VREF` to 1.8V, R4/R35 form a voltage divider between 3.3V and 1.8V, injecting current into 1.8V and biasing idle I2C lines to 2.55V.

#### Standby Control & Clock Generation
- **Sensor Standby (`/PWDN`):** J1 Pin 5 is tied directly to CM5 3.3V line `/CAM_GPIO'`. This overvoltages the 1.8V IMX219 digital I/O interface.
- **Active Oscillator X1:** 24.000 MHz active oscillator powered from 1.8V. Output feeds R10 (22Ω series damping resistor) into J1 Pin 7 (`MCLK`). Decoupling capacitor C20 is mistakenly sized at **10pF** instead of **0.1µF**, creating risk of clock jitter or startup failure.

---

### 3.4 Section 4: Mini-HDMI & SD Card

#### Mini-HDMI Interface (HDMI1)
- **Connector:** 19-pin Mini-HDMI Type-C receptacle (`Molex 47151-0001`).
- **Differential TMDS Signals:**
  - `HDMI0_TX2_P/N` -> CM5 Pins 170 / 172
  - `HDMI0_TX1_P/N` -> CM5 Pins 176 / 178
  - `HDMI0_TX0_P/N` -> CM5 Pins 182 / 184
  - `HDMI0_CLK_P/N` -> CM5 Pins 188 / 190
  - All differential pin assignments match the Raspberry Pi CM5 mezzanine specification.
- **Control & DDC:**
  - `HDMI0_CEC` -> CM5 Pin 151
  - `HDMI0_HOTPLUG` -> CM5 Pin 153 (internal 100kΩ pulldown, 5V tolerant)
  - `HDMI0_SCL` -> CM5 Pin 200 (internal 1.8kΩ pullup, 5V tolerant)
  - `HDMI0_SDA` -> CM5 Pin 199 (internal 1.8kΩ pullup, 5V tolerant)
  - Per the official Raspberry Pi CM5 Design Guide, DDC lines and HPD are 5V tolerant on CM5 and do not require external level translators.
- **Power Delivery Defect:** HDMI Pin 18 (`+5V`) is fed from U4 Pin 1 (`OUT`), which delivers 0V due to the DIO7003 pinout inversion defect.
- **Missing ESD:** TMDS lines and DDC lines lack ESD protection arrays.

#### MicroSD Card Interface (TF1)
- **Connector:** Push-push MicroSD socket (`Molex 503398-1892` / `TF-01A`).
- **Data & Clock Signals:**
  - 4-bit SD mode: DAT0 (Pin 7), DAT1 (Pin 8), DAT2 (Pin 1), DAT3 (Pin 2), CMD (Pin 3), CLK (Pin 5) connect directly to CM5 SD pins 63, 67, 69, 61, 62, 57.
  - Pinout matches CM5 SDIO controller specification.
- **Power Switching:** Pin 4 (`VDD`) is fed from U7 Pin 1 (`OUT`), delivering 0V due to the DIO7003 pinout inversion defect.
- **Card Detection:** Pin 10 (`DET_A`) is completely unconnected. Hardware hot-plug detection is disabled.
- **Signaling Override:** Pin 73 (`SD_VDD_Override`) is pulled to GND via R1 (0Ω), fixing standard 3.3V SD signaling.

---

### 3.5 Section 5: CM5 Pinout Mapping & Prioritized Wiring Defect Register

#### 40-Pin GPIO Header (PI1) Mapping Audit
All 40 pins of `PI1` were audited against standard Raspberry Pi pinout:
- Pins 1, 17: `/PWR_3V3` (3.3V Rail) — PASS
- Pins 2, 4: `/CM5_5V` (5V Rail) — PASS
- Pins 6, 9, 14, 20, 25, 30, 34, 39: `GND` — PASS
- Pins 3, 5: `GPIO2` (SDA1) / `GPIO3` (SCL1) — PASS (CM5 Pins 58 / 56)
- Pins 8, 10: `GPIO14` (TXD0) / `GPIO15` (RXD0) — PASS (CM5 Pins 55 / 51)
- Pins 19, 21, 23, 24, 26: `GPIO10` (MOSI), `GPIO9` (MISO), `GPIO11` (SCLK), `GPIO8` (CE0), `GPIO7` (CE1) — PASS
- Pins 27, 28: `ID_SD` / `ID_SC` (HAT ID EEPROM I2C) — PASS (CM5 Pins 36 / 35)
- All remaining GPIOs (4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27) match standard physical pinout.

#### Strapping & Configuration Register
- `R29` (0Ω to GND on `EEPROM_nWP`): Set to `dnp no` in schematic. Must be changed to **DNP** to allow bootloader writes.
- `R31` (0Ω to GND on `WiFi_nDisable`): Correctly marked `dnp yes` in schematic.
- `R32` (0Ω to GND on `BT_nDisable`): Correctly marked `dnp yes` in schematic.
- `R33` (0Ω to GND on `USB_OTG_ID`): Correctly marked `dnp yes` in schematic.
- `R1` (0Ω to GND on `SD_VDD_Override`): Active (`dnp no`), holds SD voltage at 3.3V.

---

## 4. Prioritized Action Checklist

1. **Immediate Schematic Bug Fixes:**
   - **U5:** Disconnect R16 and C21 from SW node. Update U5 footprint to SOT-563.
   - **U4 & U7:** Correct symbol pinout in `CM5.kicad_sym` (Pin 1=EN, 3=OUT, 4=FLG) or change MPN to `STMPS2171STR`.
   - **L1, L2, L3:** Correct symbol pinout in `CM5.kicad_sym` (Coil 1 between 1–4, Coil 2 between 2–3).
   - **Q1, Q2:** Change footprint to `Package_TO_SOT_SMD:SOT-523`.
   - **R4, R7, R35, R36:** Disconnect R4/R7 from `GPIO_VREF` and connect to `PWR_3V3`. Mark R35/R36 as DNP.
   - **J1 Pin 5:** Add resistor divider to level-shift 3.3V `CAM_GPIO` to 1.8V.
   - **X1:** Change C20 from 10pF to 0.1µF.
   - **H4 / U6:** Redesign USB selection circuit with dual-FET buffer (Q3/Q4) to allow single-switch flashing.
   - **R29:** Set property to `(dnp yes)` to prevent EEPROM write-lockout.
   - **Module1:** Split into two distinct symbols/footprints (`H1A` and `H1B`) with individual CPL centroids.
   - **Type_C1 CC Lines:** Route CC1 to CM5 Pin 96 and CC2 to CM5 Pin 94 for USB-PD 5V@5A support.

2. **PCB Layout Resolution:**
   - Re-route broken connections on `/CSI_D0_N`, `/1V2`, `/MP1658_SW`, `/MP1658_BST`, `/SDA_1V8`, and `/CM5_3V3`.
   - Perform full DRC and zone refill before production gerber generation.
