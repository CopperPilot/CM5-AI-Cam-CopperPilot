# Design Validation Progress & Violation Trend

| Run / Batch | Description | ERC Errors | ERC Warn | DRC Viol | DRC Unconnected | Parity Issues | Rule Gaps | Status |
|---|---|---|---|---|---|---|---|---|
| **Run 0 (Baseline)** | Initial project audit at `review-baseline` | 0 | 0 | 0 | 0 | 20 | 4 | FAIL (Red) |
| **Run 1 (Batch 1)** | DSI shield pin mapping, R1/R19 LCSC synchronization | 0 | 0 | 0 | 0 | 20 | 4 | In Progress |
| **Run 2 (Batch 2)** | Footprint parity, DNP attribute clearing, value sync | 0 | 0 | 0 | 0 | 0 | 4 | Parity Clean |
| **Run 3 (Batch 3)** | Custom design rule hardening (.kicad_dru), DEC logging | 0 | 0 | 0 | 0 | 0 | 0 | **PASS (Green)** |

### Trend Line Summary
- Total violations reduced from 24 (20 parity + 4 rule gaps) to **0**.
- Zero regression across all 6 copper layers.
- Full parity established between `CM5-AI-Cam-CopperPilot.kicad_sch` and `CM5-AI-Cam-CopperPilot.kicad_pcb`.
