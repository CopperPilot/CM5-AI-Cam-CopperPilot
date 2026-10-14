# CM5 AI Camera Carrier Board Project Index

## Project Overview
Carrier board designed for the Raspberry Pi Compute Module 5 (CM5), featuring an onboard 8MP Sony IMX219 camera module, Mini-HDMI video output, 15-pin DSI display connector, USB 2.0 dual-role multiplexer (USB-C flashing / vertical USB-A host), Micro SD card socket, and standard 40-pin Raspberry Pi GPIO header.

## Form Factor & Mechanics
- Dimensions: 55.0 mm x 40.0 mm
- Mounting: 4x M2.5 mounting holes matching CM5 specifications
- Corner radius: 3.0 mm

## Primary Architecture
- **Host Module:** Dual 100-pin Hirose DF40 connectors (`DF40C-100DS-0.4V(51)`)
- **Main Power:** USB Type-C 5V input with 5.1k CC pulldowns; MP1658 synchronous buck converter generating 3.3V up to 3A
- **Camera Subsystem:** Sony IMX219 with multi-rail LDOs (2.8V analog, 1.8V IO, 1.2V core), 24MHz active crystal oscillator, and MIPI CSI-2 chokes
- **USB Architecture:** FSUSB42UMX 2:1 high-speed analog switch selecting between USB-C (rpiboot flashing) and vertical USB-A (host)
- **Video & Display:** Mini-HDMI Type-C and 15-pin 1.0mm pitch horizontal FPC DSI
- **Expansion & Controls:** 40-pin GPIO header, Micro SD socket, Key1 user push-button, PWR/ACT status LEDs
