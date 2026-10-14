# CM5 AI Camera Reference Findings

## Source Information
- **Reference Target:** Waveshare Nano Base Board (C) Architecture & Schematics
- **Form Factor:** 55.0 mm x 40.0 mm matching Compute Module 5 dimensions with 3.0 mm corner radii and 4x M2.5 mounting holes
- **Target Platform:** Raspberry Pi Compute Module 5 (CM5)

## Subsystem Architecture

### 1. Compute Module 5 Mezzanine Interface
- Dual 100-pin Hirose DF40 high-density mezzanine connectors (`DF40C-100DS-0.4V(51)`).
- Input: 5V (`CM5_5V`) on power input pins 81, 83, 85, 87, 89.
- Outputs from CM5: 3.3V (`CM5_3V3`) and 1.8V (`CM5_1V8`).
- Control signals: `nRPIBOOT` (`PI_BOOT`), `RUN_PG` (`PI_RUN`), `GLOBAL_EN` (`PI_GLOBAL_EN`), `SD_PWREN`, `SD_VDD_Override`.

### 2. Onboard 8MP Camera Subsystem (IMX219-D160)
- Sensor interface: MIPI CSI-2 2-lane (`CAM0_D0_P/N`, `CAM0_D1_P/N`, `CAM0_CLK_P/N`).
- Common-mode chokes: `L1`, `L2`, `L3` (`MCF1210BF2-900T01` / `ACM1210`).
- Dedicated multi-rail power supplies:
  - `U1`: `RT9193-28GB` (2.8V LDO analog supply `VA2V8`).
  - `U2`: `RT9193-18GB` (1.8V LDO I/O supply `VO1V8`).
  - `U3`: `RT9013-12` (1.2V LDO digital core supply `VD1V2`).
- Sensor clock generation:
  - `X1`: 24.000 MHz active SMD crystal oscillator powered by 1.8V, routed through `R10` (22Ω series damping) to provide `MCLK`.
- Control & Level Translation:
  - `Q1`, `Q2`: `DMG1012T-7` dual N-MOSFETs for bidirectional 3.3V to 1.8V I2C level translation (`ID_SCL`/`ID_SDA` to `SCL_1V8`/`SDA_1V8`).
  - `CAM_GPIO`: Sensor standby/shutdown control.

### 3. Power Architecture & Load Switches
- `Type_C1`: USB Type-C receptacle providing 5V VBUS (`CM5_5V`) with dual 5.1kΩ pulldowns on CC1/CC2.
- Synchronous Buck Converter:
  - `U5`: `MP1658GTF-Z` step-down converter generating regulated 3.3V (`PWR_3V3`) at up to 3A via 4.7µH inductor `L7` (`SRP5030CC` / `SWPA6020S4R7MT`).
- Power / Load Switches:
  - `U4`: `DIO7003HCST5` supplying `HDMI_5V` with 600mA current limit.
  - `U7`: `DIO7003HCST5` supplying `SD_3.3V` controlled by `SD_PWREN`.
  - `U8`: `STMPS2171STR` supplying `USB_5V` with overcurrent fault flag to vertical USB-A socket.

### 4. USB 2.0 Multiplexing & Dual-Role Operation
- `U6`: `FSUSB42UMX` 10-pin UMLP high-speed 2:1 analog USB switch routing CM5 USB 2.0 lines:
  - Flashing / Device path to USB-C receptacle `Type_C1` for `rpiboot` eMMC firmware flashing.
  - Host path to vertical USB-A receptacle `J2` for USB peripherals.
- Selection control: Driven by `H4` boot selection jumper/switch with `Q3`/`Q4` buffer circuit.

### 5. Video, Display & Storage
- `HDMI1`: Mini-HDMI Type-C receptacle carrying CM5 HDMI differential pairs, DDC I2C, HPD, and CEC.
- `DSI1`: 15-pin 1.0mm pitch horizontal FPC connector carrying CM5 DSI 2-lane differential signals, I2C, and 3.3V power.
- `TF1`: Push-push Micro SD card socket on the left board edge for CM5 Lite modules.

### 6. Expansion & User Interface
- `PI1`: Standard 40-pin 2.54mm pitch Raspberry Pi GPIO header (2x20) with color-coded shroud.
- `Key1`: User tactile push-button connected to `GPIO21` with 10kΩ pull-up to 3.3V.
- Status LEDs: Red Power LED (`L5`) and Green Activity LED (`L6`).
