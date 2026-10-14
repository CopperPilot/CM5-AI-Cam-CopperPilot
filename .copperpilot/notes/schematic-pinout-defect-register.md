# Exhaustive Schematic Pinout and Logical Connection Audit: CM5 AI Camera Carrier Board

**Document Path:** `./.copperpilot/notes/schematic-pinout-defect-register.md`  
**Date:** 2026-10-14  
**Target Platform:** Raspberry Pi Compute Module 5 (CM5)  
**Reference Schematic:** Waveshare CM5 Nano Base Board (C) Architecture (`nano-base-board-c-sch.pdf`)  
**Design Under Audit:** `CM5-AI-Cam-CopperPilot.kicad_sch`, `CM5.kicad_sym`, and footprints in `CM5.pretty/`

---

## 1. Executive Summary

An exhaustive schematic pinout and logical connection audit of `CM5-AI-Cam-CopperPilot.kicad_sch` and its project library `CM5.kicad_sym` was performed against manufacturer component datasheets, the Raspberry Pi Compute Module 5 Design Guide, and the verified Waveshare CM5 Nano Base Board (C) reference design. 

This audit identified **10 critical, fatal, and severe defects** across power, high-speed signals, analog multiplexing, level translation, and module strapping. If fabricated in its current state, the board would experience:
1. Complete failure to enumerate USB devices on vertical USB-A (inverted polarity, power/enable inversion, and logic lockout).
2. Catastrophic overvoltage (4.84V applied to the 3.3V bus `PWR_3V3`) destroying the IMX219 camera, DSI display, MicroSD card, and 3.3V peripherals.
3. Total failure of the camera MIPI CSI-2 interface caused by differential pairs being internally short-circuited (P-to-N dead short) through common-mode chokes L1, L2, and L3.
4. Total loss of HDMI 5V power and MicroSD 3.3V power due to reversed enable/output pins on DIO7003 load switches (U4, U7).
5. Unsoldered/floating leads on I2C level shifter FETs (Q1, Q2) due to an incompatible ESD diode DFN footprint.
6. Permanent hardware lockout of CM5 Wi-Fi, Bluetooth, EEPROM writing, and USB-PD 5V@5A negotiation due to grounding strap resistors populated with 0 ohm jumpers.

---

## 2. Complete Defect Register

| Defect ID | Reference | Component Name | Severity | Primary Failure Mode | Root Cause | Exact Corrective Action |
|:---|:---|:---|:---|:---|:---|:---|
| **DEF-01** | `U6` | FSUSB42UMX (UMLP-10) | **FATAL** | Pin 8/9 inverted (VCC shorted to GND; OE tied high); Pin 6/7 inverted (D+/D- polarity swapped on USB-A Host) | Symbol in `CM5.kicad_sym` assigned Pin 8 as /OE and Pin 9 as VCC. Datasheet assigns Pin 8 as VCC and Pin 9 as /OE. Symbol also inverted HSD2+ and HSD2- on Pins 6 and 7. | In `CM5.kicad_sym`, redefine Pin 8 as VCC, Pin 9 as /OE, Pin 6 as HSD2+, Pin 7 as HSD2-. Rewire U6 so Pin 8 receives 3.3V, Pin 9 connects to GND/OE control, Pin 6 connects to USBD0_P, and Pin 7 connects to USBD0_N. |
| **DEF-02** | `U6`, `H4`, `R28` | USB Path Selection Logic | **FATAL** | Switch locked to Port 1 (USB-C); USB-A Host completely inaccessible | SEL (Pin 10) is pulled down by R28 (47k) to GND. H4 Pin 2 is GND, allowing jumpering only to GND. No 3.3V pull-up exists on SEL. Discrete Q3/Q4 buffer circuit from reference was omitted. | Rewire H4 or add pull-up: Replicate reference Q3/Q4 transistor buffer circuit (DMG1012T) or provide a 3.3V pull-up on SEL with H4 switching between 3.3V and GND, ensuring USB_SEL can be driven HIGH for USB-A Host mode. |
| **DEF-03** | `U5`, `R20`, `R21` | MP1658GTF-Z Buck Converter | **FATAL** | 4.84V catastrophic overvoltage on 3.3V bus `PWR_3V3` | R20 is set to 100k and R21 is set to 20k. With MP1658 feedback reference VFB = 0.807V, Vout = 0.807V * (1 + 100k/20k) = 4.842V. | Change R20 to **61.9kΩ** (1% tolerance) or **62kΩ** to yield Vout = 3.305V, or use MPS recommended divider Rtop = 40.2kΩ and Rbottom = 13kΩ. |
| **DEF-04** | `U5`, `C21`, `R16` | MP1658 BST Snubber Error | **CRITICAL** | High-side gate drive failure / blown internal bootstrap diode | C21 (1uF) in series with R16 (10R) is wired between BST (Pin 4) and GND. Floating high-side rail is clamped/loaded to ground. | Disconnect R16 and C21 from BST. Connect only C24 (0.1uF ceramic) between BST (Pin 4) and SW (Pin 2). If SW snubber is desired, place 330pF–1nF in series with 2–4Ω from SW (Pin 2) to GND. |
| **DEF-05** | `U5` | MP1658GTF-Z Package Mismatch | **CRITICAL** | IC cannot be soldered to PCB | MP1658GTF is an ultra-small SOT-563 package (1.6 × 1.6 mm, 0.5 mm pitch). Footprint assigned is TSOT-23-6 (2.9 × 2.8 mm, 0.95 mm pitch). | Update footprint of U5 to a standard SOT-563 / SOT-666 land pattern matching the MPS package drawing. |
| **DEF-06** | `U4`, `U7` | DIO7003HCST5 (SOT-23-5) | **FATAL** | Zero power output on Mini-HDMI 5V (U4) and MicroSD 3.3V (U7) | Symbol in `CM5.kicad_sym` uses TPS2051 pinout (Pin 1=OUT, Pin 3=FAULT, Pin 4=EN). DIO7003 SOT-23-5 datasheet is Pin 1=EN, Pin 2=GND, Pin 3=OUT, Pin 4=FLG, Pin 5=IN. Output load is wired to EN gate; enable signal is wired to open-drain flag. | Correct `DIO7003HCST5` symbol in `CM5.kicad_sym`: Pin 1 = EN, Pin 2 = GND, Pin 3 = OUT, Pin 4 = FLG, Pin 5 = IN. Rewire U4 and U7 so Pin 1 connects to enable control, Pin 3 connects to power output, Pin 4 connects to fault flag. |
| **DEF-07** | `L1`, `L2`, `L3` | MCF1210BF2-900T01 Chokes | **FATAL** | Dead short on all MIPI CSI-2 data and clock pairs (P shorted to N) | Footprint `CM5:L_CommonModeChoke_Coilank_ACM1210` numbers pads counter-clockwise (1=TL, 2=BL, 3=BR, 4=TR). Choke internal coils run horizontally (1 to 4, 2 to 3). Symbol maps coils between 1–2 and 4–3. Result: Coil A shorts CAM0_D0_P to CAM0_D0_N; Coil B shorts CSI_D0_P to CSI_D0_N. | Redefine symbol or footprint: In `CM5.kicad_sym` for `MCF1210BF2-900T01`, define Coil 1 between Pin 1 and Pin 4, and Coil 2 between Pin 2 and Pin 3. Or remap footprint pad numbers to match through-routing. |
| **DEF-08** | `Q1`, `Q2` | DMG1012T (SOT-523) | **CRITICAL** | Transistor leads cannot solder to PCB; pins float or bridge | Footprint assigned is `CM5:Texas_DRT-3` (1.0 × 0.8 mm leadless DFN intended for TI TPD2EUSB30 ESD diode). DMG1012T is a gull-wing SOT-523 package (1.6 × 0.8 mm). | Change footprint of Q1 and Q2 from `CM5:Texas_DRT-3` to standard `Package_TO_SOT_SMD:SOT-523` (or project SOT-523). |
| **DEF-09** | `R4`, `R7`, `R35`, `R36` | I2C Level Shifter Pull-Ups | **HIGH** | Cross-rail voltage contention between 3.3V and 1.8V | SCL0 has R35 (4.7k to PWR_3V3) in parallel with R4 (4.7k to GPIO_VREF). SDA0 has R36 (4.7k to PWR_3V3) in parallel with R7 (4.7k to GPIO_VREF). When H5 selects 1.8V for GPIO_VREF, a 3.3V-to-1.8V resistive divider is created. | Disconnect R4 and R7 from GPIO_VREF and tie their high side cleanly to PWR_3V3, or eliminate redundant pull-up resistors R35/R36 on DSI1 so that each I2C line has only a single 4.7k pull-up to the active bus voltage. |
| **DEF-10** | `Module1` | ComputeModule5-CM5 (H1A/H1B) | **MEDIUM** | ERC `pin_to_pin` errors; CM5 USB-PD 5V@5A negotiation disabled | Pins 84 & 86 (+3.3V) and Pins 88 & 90 (+1.8V) are all typed as `Power output`, triggering ERC conflicts. CM5 CC1 (Pin 94) and CC2 (Pin 96) are left disconnected. | Change Pin 86 and Pin 90 to `passive` in `ComputeModule5-CM5` symbol. Connect Type-C CC1 to Pin 94 and CC2 to Pin 96 to enable CM5 onboard PMIC USB-PD 5V@5A negotiation. |
| **DEF-11** | `R29`, `R31`, `R32`, `R33` | Strapping Resistors Populated | **HIGH** | CM5 Wi-Fi disabled, Bluetooth disabled, EEPROM write-protected, USB recovery blocked | R31 pulls Pin 89 (WiFi_nDisable) to GND. R32 pulls Pin 91 (BT_nDisable) to GND. R29 pulls Pin 20 (EEPROM_nWP) to GND. R33 pulls Pin 101 (USB_OTG_ID) to GND. | Mark R29, R31, R32, and R33 as **DNP** (Do Not Populate) in the schematic and BOM. These pins must float high via CM5 internal pull-ups for normal operation. |
| **DEF-12** | `#FLG03`–`#FLG08`, `J2`, `PI1` | Power Flag & Connector Pin Types | **MEDIUM** | 8 ERC Errors and 12 ERC Warnings on power distribution | PWR_FLAGs placed on outputs of U1, U2, U3, U4, U7, U8 which are already `power_out`. J2 Pin 1 is typed `Power output`, colliding with U8 Pin 1. PI1 power pins are typed `Bidirectional`. | Delete `#FLG03`, `#FLG04`, `#FLG05`, `#FLG06`, `#FLG07`, `#FLG08`. Change J2 Pin 1 to `power_in` or `passive`. Change PI1 power pins to `power_in` or `passive`. |

---

## 3. Detailed Component Deep-Dive Analysis

### 3.1 FSUSB42UMX (U6) Multiplexer & USB Switching Logic

#### Datasheet vs Schematic Comparison
The FSUSB42UMX is an onsemi high-speed USB 2.0 dual DPDT switch in a 10-lead UMLP package (1.4 × 1.8 mm, 0.4 mm pitch, CASE 523BC).

```
   Official UMLP-10 Top View:
             Pin 1 (D+)       Pin 10 (SEL)
                ┌─────────────┐
   Pin 2 (D-)   │             │ Pin 9 (/OE)
   Pin 3 (GND)  │   FSUSB42   │ Pin 8 (VCC)
   Pin 4 (HSD1-)│    UMLP     │ Pin 7 (HSD2-)
   Pin 5 (HSD1+)│             │ Pin 6 (HSD2+)
                └─────────────┘
```

1. **Pins 8 & 9 Inversion:**
   - In `CM5.kicad_sym`: Pin 8 is defined as `/OE` (input), Pin 9 is defined as `VCC` (power_in).
   - In Datasheet: Pin 8 is **VCC**, Pin 9 is **/OE**.
   - Netlist Consequence: In the schematic, Pin 8 is connected to `GND`, and Pin 9 is connected to `CM5_3V3`. On the physical PCB, `VCC` (Pin 8) is shorted directly to `GND`, and `/OE` (Pin 9) is tied to 3.3V (holding the switch disabled). The chip has zero power and is disabled.
2. **Pins 6 & 7 Inversion:**
   - In `CM5.kicad_sym`: Pin 6 is defined as `HSD2-`, Pin 7 is defined as `HSD2+`.
   - In Datasheet: Pin 6 is **HSD2+**, Pin 7 is **HSD2-**.
   - Netlist Consequence: Net `USBD0_N` (J2 D-) is connected to Pin 6 (physically HSD2+), and Net `USBD0_P` (J2 D+) is connected to Pin 7 (physically HSD2-). When switched to Host mode, USB differential polarity is flipped, preventing USB device enumeration.
3. **Control Truth Table & Lockout:**
   - Truth Table: When `SEL` = 0, D± connects to HSD1± (Type-C). When `SEL` = 1, D± connects to HSD2± (USB-A Host).
   - In schematic: Pin 10 (`SEL`) is pulled down to GND via R28 (47kΩ).
   - Jumper H4: Pin 1 = `PI_BOOT`, Pin 2 = `GND`, Pin 3 = `USB_SEL`. Jumpering Pin 2 to Pin 3 pulls `USB_SEL` to GND. There is no pull-up to 3.3V anywhere on `USB_SEL`. Therefore, `USB_SEL` can NEVER be driven HIGH. The multiplexer is permanently trapped in USB-C flashing mode.

---

### 3.2 MP1658GTF-Z Synchronous Buck Converter (U5)

#### Feedback Divider & Overvoltage Risk
The MP1658 is an MPS 16V, 3A, 600kHz synchronous step-down converter with an internal reference voltage of \(V_{\text{FB}} = 0.807\text{ V}\).

The output voltage equation is:
\[
V_{\text{OUT}} = V_{\text{FB}} \times \left(1 + \frac{R_{\text{TOP}}}{R_{\text{BOTTOM}}}\right)
\]

In `CM5-AI-Cam-CopperPilot.kicad_sch`:
- \(R_{\text{TOP}} = R_{20} = 100\text{ k}\Omega\)
- \(R_{\text{BOTTOM}} = R_{21} = 20\text{ k}\Omega\)
- Output Voltage:
\[
V_{\text{OUT}} = 0.807\text{ V} \times \left(1 + \frac{100}{20}\right) = 0.807\text{ V} \times 6 = 4.842\text{ V}
\]

Applying **4.84V** to `PWR_3V3` exceeds the absolute maximum rating of the Raspberry Pi CM5 3.3V IO (3.6V max), the Sony IMX219 sensor IO, the DSI display driver IC, and the MicroSD card (3.6V max), resulting in catastrophic hardware failure.

#### Bootstrap / Snubber Wiring Error
- In the schematic: R16 (10Ω) and C21 (1µF) are connected between `BST` (Pin 4) and `GND`.
- The bootstrap circuit requires a floating capacitor between `BST` and `SW` to provide gate drive voltage above `VIN` for the internal high-side N-channel MOSFET.
- Grounding `BST` through a 1µF capacitor clamps the bootstrap node to ground during SW transitions, depriving the high-side gate driver of charge and causing excessive switch node dissipation or PMIC destruction.
- Correct configuration: C24 (0.1µF ceramic, 16V or 25V) connects between `BST` (Pin 4) and `SW` (Pin 2). C21 and R16 must be disconnected from `BST`.

#### Package Mismatch
- `MP1658GTF-Z` comes in an **SOT-563** package (body dimensions 1.6 × 1.2 mm, 0.5 mm lead pitch).
- The board assigns footprint `CM5:TSOT-23-6` (body dimensions 2.9 × 1.6 mm, 0.95 mm lead pitch).
- The assigned footprint has nearly double the lead pitch and pad spacing of the actual component.

---

### 3.3 DIO7003HCST5 (U4, U7) & STMPS2171STR (U8) Load Switches

#### DIO7003HCST5 Pin Inversion
The DIO7003HCST5 is a SOT-23-5 high-side power distribution switch.
- Official Datasheet Pinout:
  - Pin 1: `EN` (Active High Enable)
  - Pin 2: `GND`
  - Pin 3: `OUT` (Switched Power Output)
  - Pin 4: `FLG` (Fault Status Flag, Open-Drain)
  - Pin 5: `IN` (Input Voltage)
- Schematic Symbol (`CM5.kicad_sym:DIO7003HCST5`):
  - Pin 1: `OUT`
  - Pin 2: `GND`
  - Pin 3: `FAULT`
  - Pin 4: `EN`
  - Pin 5: `IN`

**Result on U4 (HDMI 5V) and U7 (SD 3.3V):**
- Physical Pin 1 (EN) is connected to the load nets (`HDMI_5V`, `SD_3.3V`).
- Physical Pin 3 (OUT) is connected to the open-drain FAULT line (left floating).
- Physical Pin 4 (FLG) is connected to the enable control nets (`SD_PWREN`, R14 pull-up).
- The switches cannot turn on. Mini-HDMI Pin 18 receives 0V, and MicroSD Pin 4 receives 0V.

#### STMPS2171STR Pinout Verification
- STMicroelectronics STMPS2171STR SOT-23-5L Pinout:
  - Pin 1: `OUT`
  - Pin 2: `GND`
  - Pin 3: `FAULT`
  - Pin 4: `EN`
  - Pin 5: `IN`
- Symbol matches physical component; however, J2 Pin 1 is mistakenly typed `Power output`, creating an ERC conflict with U8 Pin 1 (`OUT`).

---

### 3.4 Common-Mode Chokes (L1, L2, L3) Differential Short

#### Layout and Coil Mapping
Common-mode chokes L1, L2, and L3 are specified as Coilank `ACM1210` / `MCF1210BF2-900T01` (1.2 × 1.0 mm SMD common-mode filters).

```
   Physical Choke Internal Construction:
        Pad 1 (Top-Left)  ─────── Coil A ─────── Pad 4 (Top-Right)
        Pad 2 (Bot-Left)  ─────── Coil B ─────── Pad 3 (Bot-Right)
```

Footprint `CM5:L_CommonModeChoke_Coilank_ACM1210` assigns pad numbers:
- Pad 1 = Top-Left
- Pad 2 = Bottom-Left
- Pad 3 = Bottom-Right
- Pad 4 = Top-Right

Schematic symbol `CM5.kicad_sym:MCF1210BF2-900T01` defines:
- Coil 1 across Pin 1 and Pin 2
- Coil 2 across Pin 4 and Pin 3

Schematic wiring for L1 (CSI Lane 0):
- Net `CAM0_D0_P` connects to Pin 1 (Pad 1, Top-Left)
- Net `CAM0_D0_N` connects to Pin 4 (Pad 4, Top-Right)
- Net `CSI_D0_P` connects to Pin 2 (Pad 2, Bottom-Left)
- Net `CSI_D0_N` connects to Pin 3 (Pad 3, Bottom-Right)

**The Failure:**
- Physical Coil A connects Pad 1 directly to Pad 4. On the schematic, Pad 1 is `CAM0_D0_P` and Pad 4 is `CAM0_D0_N`. Coil A directly shorts `CAM0_D0_P` to `CAM0_D0_N`!
- Physical Coil B connects Pad 2 directly to Pad 3. On the schematic, Pad 2 is `CSI_D0_P` and Pad 3 is `CSI_D0_N`. Coil B directly shorts `CSI_D0_P` to `CSI_D0_N`!
- The identical short exists on L2 (`CAM0_D1_P` shorted to `CAM0_D1_N`) and on L3 (`CAM0_CLK_P` shorted to `CAM0_CLK_N`).
- **Effect:** Zero differential video signal reaches the CM5. High-speed MIPI CSI-2 transmission fails 100%.

---

### 3.5 I2C Level Shifter (Q1, Q2) & Pull-Up Network

1. **Footprint Mismatch:**
   - Component: `DMG1012T-7` (Diodes Inc. N-channel MOSFET in SOT-523 package; dimensions 1.6 × 1.6 mm including gull-wing leads).
   - Assigned Footprint: `CM5:Texas_DRT-3` (TI DRT leadless DFN package; dimensions 1.0 × 0.8 mm, designed for `TPD2EUSB30` TVS diodes).
   - The SOT-523 transistor leads will sit completely outside the DRT-3 pads, resulting in unsoldered open circuits.
2. **Dual-Rail Pull-Up Contention:**
   - Q1/Q2 gates are powered from 1.8V (`VO1V8`).
   - SCL0 is pulled up by R35 (4.7kΩ to `PWR_3V3`) AND by R4 (4.7kΩ to `GPIO_VREF`).
   - SDA0 is pulled up by R36 (4.7kΩ to `PWR_3V3`) AND by R7 (4.7kΩ to `GPIO_VREF`).
   - Jumper H5 allows selecting either 3.3V or 1.8V for `GPIO_VREF`.
   - When H5 is set to 1.8V, R4 forms a voltage divider between 3.3V and 1.8V, injecting current into the 1.8V supply and corrupting the logic high threshold.
   - Corrective action: Connect R4 and R7 pull-ups strictly to the 3.3V bus, and eliminate redundant resistors R35 and R36.

---

### 3.6 CM5 Mezzanine Interface (H1A / H1B) & Strapping Configuration

1. **ERC Pin Conflicts in `ComputeModule5-CM5`:**
   - Pin 84 is typed `power_out`, and Pin 86 is typed `power_out`. Connecting both to net `/CM5_3V3` produces an ERC error. Change Pin 86 to `passive`.
   - Pin 88 is typed `power_out`, and Pin 90 is typed `power_out`. Connecting both to net `/CM5_1V8` produces an ERC error. Change Pin 90 to `passive`.
2. **USB-PD CC Lines Disconnected:**
   - CM5 Pin 94 is `CC1` (AnalogIP1) and Pin 96 is `CC2` (AnalogIP0).
   - In `CM5-AI-Cam-CopperPilot.kicad_sch`, Pins 94 and 96 are unconnected, while Type_C1 has static 5.1kΩ pulldowns R2/R3.
   - Without routing CC1/CC2 to the CM5 PMIC, the module cannot negotiate 5V @ 5A from official Raspberry Pi 27W USB-PD supplies.
3. **Hardwired Disable Straps (R29, R31, R32, R33):**
   - R31 (0Ω) grounds Pin 89 (`WiFi_nDisable`), permanently disabling onboard Wi-Fi.
   - R32 (0Ω) grounds Pin 91 (`BT_nDisable`), permanently disabling onboard Bluetooth.
   - R29 (0Ω) grounds Pin 20 (`EEPROM_nWP`), write-protecting the module EEPROM.
   - R33 (0Ω) grounds Pin 101 (`USB_OTG_ID`), forcing host mode on USB0.
   - All four resistors must be designated **DNP** in the schematic.

---

## 4. Exact Corrective Action Checklist

1. **FSUSB42UMX (U6):**
   - Edit symbol `FSUSB42MX` in `CM5.kicad_sym`:
     - Pin 8 -> Name: `VCC`, Type: `power_in`
     - Pin 9 -> Name: `/OE`, Type: `input`
     - Pin 6 -> Name: `HSD2+`, Type: `bidirectional`
     - Pin 7 -> Name: `HSD2-`, Type: `bidirectional`
   - In schematic:
     - Connect Pin 8 to Net `/CM5_3V3`.
     - Connect Pin 9 to GND (or enable control).
     - Connect Pin 6 to Net `/USBD0_P` (J2 Pin 3).
     - Connect Pin 7 to Net `/USBD0_N` (J2 Pin 2).
   - Fix H4 selection logic to provide an active pull-up to 3.3V so `USB_SEL` can toggle between 0 and 1.
2. **Buck Converter (U5):**
   - Replace R20 (100kΩ) with **61.9kΩ 1%** (or Rtop = 40.2kΩ, Rbottom = 13kΩ).
   - Remove R16 (10Ω) and C21 (1µF) from Pin 4 (`BST`).
   - Retain only C24 (0.1µF) connected directly across Pin 4 (`BST`) and Pin 2 (`SW`).
   - Update footprint from `CM5:TSOT-23-6` to an accurate `SOT-563` land pattern.
3. **Power Switches (U4, U7):**
   - Edit symbol `DIO7003HCST5` in `CM5.kicad_sym`:
     - Pin 1 -> Name: `EN`, Type: `input`
     - Pin 2 -> Name: `GND`, Type: `power_in`
     - Pin 3 -> Name: `OUT`, Type: `power_out`
     - Pin 4 -> Name: `FLG`, Type: `open_collector`
     - Pin 5 -> Name: `IN`, Type: `power_in`
   - In schematic:
     - U4: Pin 1 to R14/HDMI_EN, Pin 3 to Net `/HDMI_5V`, Pin 4 to NC/testpad.
     - U7: Pin 1 to Net `/SD_PWREN`, Pin 3 to Net `/SD_3.3V`, Pin 4 to NC/testpad.
4. **Common-Mode Chokes (L1, L2, L3):**
   - Update symbol `MCF1210BF2-900T01` so that Coil 1 connects Pin 1 to Pin 4, and Coil 2 connects Pin 2 to Pin 3.
   - Verify layout connectivity: differential signals must pass straight through from input to output without cross-shorting.
5. **Level Shifters (Q1, Q2):**
   - Change footprint of Q1 and Q2 to standard `Package_TO_SOT_SMD:SOT-523`.
   - Remove redundant pull-ups R35 and R36 on DSI1, or disconnect R4 and R7 from `GPIO_VREF` and connect to `PWR_3V3`.
6. **CM5 Mezzanine (Module1):**
   - In `CM5.kicad_sym` symbol `ComputeModule5-CM5`:
     - Change Pin 86 (`+3.3v_(Output)`) electrical type from `power_out` to `passive`.
     - Change Pin 90 (`+1.8v_(Output)`) electrical type from `power_out` to `passive`.
   - Mark R1, R29, R31, R32, R33 as **DNP**.
   - Connect Type_C1 CC1/CC2 to Module1 Pins 94 and 96.
7. **ERC Cleanup:**
   - Remove spurious `PWR_FLAG` symbols `#FLG03`, `#FLG04`, `#FLG05`, `#FLG06`, `#FLG07`, `#FLG08`.
   - Change J2 Pin 1 (`VBUS`) in `USB_A_Vertical` from `power_out` to `passive` or `power_in`.
   - In `Raspberry_Pi_40Pin_GPIO`, change power pins (1, 2, 4, 6, 9, 14, 17, 20, 25, 30, 34, 39) to `power_in` or `passive`.
   - Re-route U1 input inductor FB1 to `CM5_5V` for high PSRR camera analog power.
