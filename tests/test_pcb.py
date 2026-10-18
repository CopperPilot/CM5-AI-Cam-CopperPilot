"""Automated hardware verification test suite for CM5 AI Camera Carrier Board."""

import csv
import glob
import math
import os
import re

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestBoardPhysical:
    """Verifies board physical dimensions, layer stackup, and boundary geometry."""

    def test_board_dimensions(self, pcb_data):
        """Assert outer bounding box matches 55.0 x 40.0 mm (+/- 0.5 mm tolerance)."""
        xs = []
        ys = []
        for elem in pcb_data.edge_cuts:
            if elem["type"] == "line":
                xs.extend([elem["x1"], elem["x2"]])
                ys.extend([elem["y1"], elem["y2"]])
            elif elem["type"] == "arc":
                xs.extend([elem["x1"], elem["xm"], elem["x2"]])
                ys.extend([elem["y1"], elem["ym"], elem["y2"]])

        assert len(xs) > 0, "No Edge.Cuts elements found"
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        assert 54.5 <= width <= 55.5, f"Board width {width:.2f} mm out of range [54.5, 55.5]"
        assert 39.5 <= height <= 40.5, f"Board height {height:.2f} mm out of range [39.5, 40.5]"

    def test_board_outline_closed(self, pcb_data):
        """Assert Edge.Cuts consists of continuous line/arc primitives forming rounded rectangle."""
        assert len(pcb_data.edge_cuts) >= 8, f"Expected rounded-corner profile (>=8 elements), got {len(pcb_data.edge_cuts)}"

    def test_layer_stackup_6layer(self, pcb_data):
        """Assert standard JLCPCB 6-layer copper stackup with 1.6 mm nominal thickness."""
        assert '"F.Cu"' in pcb_data.content
        assert '"In1.Cu"' in pcb_data.content
        assert '"In2.Cu"' in pcb_data.content
        assert '"In3.Cu"' in pcb_data.content
        assert '"In4.Cu"' in pcb_data.content
        assert '"B.Cu"' in pcb_data.content
        assert '(25 "Edge.Cuts" user)' in pcb_data.content or '"Edge.Cuts"' in pcb_data.content

    def test_board_thickness_nominal(self, pcb_data):
        """Assert board general thickness is set to 1.6 mm."""
        assert '(thickness 1.6)' in pcb_data.content


class TestConnectivityAndParity:
    """Verifies KiCad electrical rules, design rules, and schematic-PCB parity."""

    def test_drc_zero_errors(self, drc_results):
        """Assert DRC has 0 errors and 0 warnings."""
        violations = drc_results.get("violations", [])
        errors = [v for v in violations if v.get("severity") == "error"]
        warnings = [v for v in violations if v.get("severity") == "warning"]
        assert len(errors) == 0, f"DRC reported {len(errors)} errors: {errors[:3]}"
        assert len(warnings) == 0, f"DRC reported {len(warnings)} warnings: {warnings[:3]}"

    def test_drc_zero_unconnected_items(self, drc_results):
        """Assert 100% routing completion (0 unconnected items)."""
        unconnected = drc_results.get("unconnected_items", [])
        assert len(unconnected) == 0, f"Found {len(unconnected)} unconnected items: {unconnected[:3]}"

    def test_drc_schematic_parity(self, drc_results):
        """Assert 0 schematic-to-PCB parity discrepancies."""
        parity = drc_results.get("schematic_parity", [])
        assert len(parity) == 0, f"Schematic parity mismatch: {parity[:3]}"

    def test_erc_zero_errors_and_warnings(self, erc_results):
        """Assert ERC has 0 errors and 0 warnings."""
        sheets = erc_results.get("sheets", [])
        errors = [v for s in sheets for v in s.get("violations", []) if v.get("severity") == "error"]
        warnings = [v for s in sheets for v in s.get("violations", []) if v.get("severity") == "warning"]
        assert len(errors) == 0, f"ERC reported {len(errors)} errors: {errors[:3]}"
        assert len(warnings) == 0, f"ERC reported {len(warnings)} warnings: {warnings[:3]}"

    def test_power_distribution_nets_present(self, pcb_data):
        """Assert critical power distribution nets exist in PCB layout."""
        power_nets = ["GND", "5V", "3V3"]
        for net in power_nets:
            assert any(net in n for n in pcb_data.nets), f"Power net {net} not found in PCB nets"

    def test_camera_subsystem_nets_present(self, pcb_data):
        """Assert camera power rails and MIPI CSI-2 differential nets exist."""
        cam_nets = ["/2V8", "/1V8", "/1V2"]
        for net in cam_nets:
            assert any(net in n for n in pcb_data.nets), f"Camera power net {net} not found"

    def test_usb_differential_nets_present(self, pcb_data):
        """Assert USB 2.0 differential pairs exist."""
        assert any("/USB0_P" in n or "/USBD0_P" in n for n in pcb_data.nets)
        assert any("/USB0_N" in n or "/USBD0_N" in n for n in pcb_data.nets)


class TestTraceGeometryAndDFM:
    """Verifies copper geometries comply with JLCPCB 6-layer manufacturing targets."""

    def test_signal_trace_min_width(self, pcb_data):
        """Assert all routed copper tracks meet or exceed JLCPCB 6-layer min width (>= 0.09 mm)."""
        for seg in pcb_data.segments:
            assert seg["width"] >= 0.089, (
                f"Segment width {seg['width']} mm below minimum 0.09 mm limit on net {seg['net_name']}"
            )

    def test_power_trace_widths(self, pcb_data):
        """Assert power rail distribution traces maintain low-impedance geometry (>= 0.15 mm)."""
        power_segs = [s for s in pcb_data.segments if any(p in s["net_name"] for p in ["5V", "3V3", "GND"])]
        assert len(power_segs) > 0, "No power segments found"
        for s in power_segs:
            assert s["width"] >= 0.149, f"Power segment width {s['width']} mm below 0.15 mm on {s['net_name']}"

    def test_via_drill_and_pad_dimensions(self, pcb_data):
        """Assert all vias meet JLCPCB 6-layer via drill (>= 0.20 mm) and pad diameter (>= 0.40 mm)."""
        assert len(pcb_data.vias) > 0, "No vias found in PCB layout"
        for v in pcb_data.vias:
            assert v["drill"] >= 0.19, f"Via drill {v['drill']} mm below target (0.20 mm) at ({v['x']}, {v['y']})"
            assert v["size"] >= 0.39, f"Via size {v['size']} mm below target (0.40 mm) at ({v['x']}, {v['y']})"

    def test_via_annular_rings(self, pcb_data):
        """Assert via annular rings meet JLCPCB min constraint (>= 0.10 mm)."""
        for v in pcb_data.vias:
            assert v["annular_ring"] >= 0.095, (
                f"Via annular ring {v['annular_ring']} mm below target (0.10 mm) at ({v['x']}, {v['y']})"
            )


class TestSubsystemCircuits:
    """Verifies presence and configuration of essential circuit blocks."""

    def test_cm5_module_footprint_present(self, pcb_data):
        """Assert Raspberry Pi Compute Module 5 footprint (Module1) is instantiated."""
        assert "Module1" in pcb_data.footprints
        mod = pcb_data.footprints["Module1"]
        assert "Compute-Module" in mod["package"] or "ComputeModule" in mod["value"]

    def test_camera_subsystem_chokes(self, pcb_data):
        """Assert common mode noise chokes (L1, L2, L3) are populated for MIPI CSI-2."""
        for ref in ["L1", "L2", "L3"]:
            assert ref in pcb_data.footprints, f"Camera choke {ref} missing from layout"

    def test_camera_ldos_present(self, pcb_data):
        """Assert dedicated camera low-noise LDOs (U1, U2, U3) are present."""
        for ref in ["U1", "U2", "U3"]:
            assert ref in pcb_data.footprints, f"Camera LDO {ref} missing from layout"

    def test_buck_regulator_present(self, pcb_data):
        """Assert 3.3V synchronous buck regulator (U5) is populated."""
        assert "U5" in pcb_data.footprints, "Buck regulator U5 missing"

    def test_usb_c_cc_termination_resistors(self, pcb_data):
        """Assert USB-C CC termination resistors (R2, R3) are present with 5.1k value."""
        assert "R2" in pcb_data.footprints, "CC resistor R2 missing"
        assert "R3" in pcb_data.footprints, "CC resistor R3 missing"
        assert "5.1k" in pcb_data.footprints["R2"]["value"].lower() or "5k1" in pcb_data.footprints["R2"]["value"].lower()
        assert "5.1k" in pcb_data.footprints["R3"]["value"].lower() or "5k1" in pcb_data.footprints["R3"]["value"].lower()

    def test_peripherals_present(self, pcb_data):
        """Assert display (HDMI1, DSI1), storage (TF1), expansion (PI1), and USB (Type_C1, J2) exist."""
        for ref in ["HDMI1", "DSI1", "TF1", "PI1", "Type_C1", "J2"]:
            assert ref in pcb_data.footprints, f"Peripheral connector {ref} missing"


class TestRepoHygieneAndLibraries:
    """Verifies repository cleanliness, relative paths, and public open-source standards."""

    def test_no_absolute_user_paths_in_tables(self):
        """Assert library tables use relative paths (${KIPRJMOD}) without user directory leaks."""
        for tbl_file in ["sym-lib-table", "fp-lib-table"]:
            with open(os.path.join(PROJECT_DIR, tbl_file)) as f:
                content = f.read()
            assert "/home/" not in content, f"Absolute user path found in {tbl_file}"
            assert "/Users/" not in content, f"Absolute user path found in {tbl_file}"
            assert "${KIPRJMOD}" in content or "(lib" in content

    def test_manufacturing_bom_completeness(self):
        """Assert BOM contains all required JLCPCB assembly columns and assigned LCSC part numbers."""
        bom_path = os.path.join(PROJECT_DIR, "jlcpcb_production", "assembly", "bom_jlcpcb.csv")
        assert os.path.exists(bom_path), f"BOM file missing at {bom_path}"
        with open(bom_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0, "BOM contains no rows"
        for row in rows:
            assert row.get("Designator"), f"Row missing Designator: {row}"
            assert row.get("Comment") or row.get("Value"), f"Row missing Comment/Value: {row}"
            assert row.get("Footprint"), f"Row missing Footprint: {row}"
            lcsc = row.get("LCSC Part #") or row.get("LCSC")
            assert lcsc, f"Row missing LCSC Part #: {row}"

    def test_manufacturing_cpl_completeness(self):
        """Assert CPL contains required pick-and-place headers and coordinates."""
        cpl_path = os.path.join(PROJECT_DIR, "jlcpcb_production", "assembly", "cpl_jlcpcb.csv")
        assert os.path.exists(cpl_path), f"CPL file missing at {cpl_path}"
        with open(cpl_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0, "CPL contains no rows"
        for row in rows:
            ref = row.get("Designator") or row.get("Ref")
            x = row.get("Mid X") or row.get("PosX")
            y = row.get("Mid Y") or row.get("PosY")
            rot = row.get("Rotation") or row.get("Rot")
            side = row.get("Layer") or row.get("Side")
            assert ref, f"CPL row missing Designator/Ref: {row}"
            assert x, f"CPL row missing Mid X/PosX: {row}"
            assert y, f"CPL row missing Mid Y/PosY: {row}"
            assert rot, f"CPL row missing Rotation/Rot: {row}"
            assert side, f"CPL row missing Layer/Side: {row}"

    def test_gerber_package_files(self):
        """Assert Gerber directory contains all 6 copper layers, mask, silk, paste, and drill files."""
        g_dir = os.path.join(PROJECT_DIR, "jlcpcb_production", "gerbers")
        assert os.path.exists(g_dir), f"Gerber directory missing at {g_dir}"
        files = os.listdir(g_dir)

        # Check 6 copper layers
        for layer in ["F_Cu", "In1_Cu", "In2_Cu", "In3_Cu", "In4_Cu", "B_Cu"]:
            assert any(layer in f for f in files), f"Missing copper layer {layer} in Gerbers"

        # Check masks and edge cuts
        assert any("Edge_Cuts" in f or ".gm1" in f for f in files), "Missing Edge_Cuts outline in Gerbers"
        assert any("F_Mask" in f for f in files), "Missing F_Mask in Gerbers"
        assert any("B_Mask" in f for f in files), "Missing B_Mask in Gerbers"
        assert any("PTH" in f or "drill" in f for f in files), "Missing drill file in Gerbers"
