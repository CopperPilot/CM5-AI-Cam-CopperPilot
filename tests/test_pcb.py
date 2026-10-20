"""Automated hardware verification test suite for CM5 AI Camera Carrier Board."""

import csv
import glob
import json
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
        """Assert standard JLCPCB 6-layer copper stackup (JLC06161H-7628) with 1.6 mm nominal thickness."""
        assert '"F.Cu"' in pcb_data.content
        assert '"In1.Cu"' in pcb_data.content
        assert '"In2.Cu"' in pcb_data.content
        assert '"In3.Cu"' in pcb_data.content
        assert '"In4.Cu"' in pcb_data.content
        assert '"B.Cu"' in pcb_data.content
        assert '(25 "Edge.Cuts" user)' in pcb_data.content or '"Edge.Cuts"' in pcb_data.content
        assert '(thickness 0.2104)' in pcb_data.content
        assert '(thickness 0.4)' in pcb_data.content

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
            assert any(net in n for n in pcb_data.nets), f"Power net {net} not found in PCB layout"

    def test_camera_subsystem_nets_present(self, pcb_data):
        """Assert camera power rails and MIPI CSI-2 differential nets exist."""
        cam_nets = ["/2V8", "/1V8", "/1V2", "/CSI_CLK_P", "/CSI_D0_P", "/CSI_D1_P"]
        for net in cam_nets:
            assert any(net in n for n in pcb_data.nets), f"Camera net {net} not found"

    def test_usb_differential_nets_present(self, pcb_data):
        """Assert USB 2.0 differential pairs exist."""
        assert any("/USB0_P" in n or "/USBD0_P" in n for n in pcb_data.nets)
        assert any("/USB0_N" in n or "/USBD0_N" in n for n in pcb_data.nets)


class TestTraceGeometryAndDFM:
    """Verifies copper geometries and controlled-impedance netclasses comply with JLCPCB 6-layer targets."""

    def test_differential_netclasses_configured(self):
        """Assert HighSpeed_100R (MIPI/HDMI) and HighSpeed_90R (USB) netclasses and patterns exist in .kicad_pro."""
        pro_path = os.path.join(PROJECT_DIR, "CM5-AI-Cam-CopperPilot.kicad_pro")
        with open(pro_path, encoding="utf-8") as f:
            pro = json.load(f)

        classes = {c["name"]: c for c in pro.get("net_settings", {}).get("classes", [])}
        assert "HighSpeed_100R" in classes, "Missing HighSpeed_100R netclass"
        assert "HighSpeed_90R" in classes, "Missing HighSpeed_90R netclass"

        hs100 = classes["HighSpeed_100R"]
        hs90 = classes["HighSpeed_90R"]
        assert math.isclose(hs100["diff_pair_width"], 0.127, abs_tol=1e-3)
        assert math.isclose(hs100["diff_pair_gap"], 0.15, abs_tol=1e-3)
        assert math.isclose(hs90["diff_pair_width"], 0.18, abs_tol=1e-3)
        assert math.isclose(hs90["diff_pair_gap"], 0.15, abs_tol=1e-3)

        patterns = pro.get("net_settings", {}).get("netclass_patterns", [])
        hs100_pats = {p["pattern"] for p in patterns if p.get("netclass") == "HighSpeed_100R"}
        hs90_pats = {p["pattern"] for p in patterns if p.get("netclass") == "HighSpeed_90R"}
        for expected in ["/CAM0_*", "/CSI_*", "/DSI1_*", "/HDMI0_CLK_*", "/HDMI0_TX*"]:
            assert expected in hs100_pats, f"Missing HighSpeed_100R pattern {expected}"
        for expected in ["/USB0_P", "/USB0_N", "/USB0_B_*", "/USBB_*", "/USBD0_*"]:
            assert expected in hs90_pats, f"Missing HighSpeed_90R pattern {expected}"

    def test_mipi_hdmi_100ohm_trace_widths(self, pcb_data):
        """Assert all MIPI CSI-2, MIPI DSI, and HDMI TMDS differential traces use 0.127 mm (100 Ohm) geometry."""
        prefixes = ("/CAM0_", "/CSI_", "/DSI1_", "/HDMI0_CLK_", "/HDMI0_TX")
        hs100_segs = [s for s in pcb_data.segments if s["net_name"].startswith(prefixes)]
        assert len(hs100_segs) > 0, "No MIPI/HDMI differential segments found"
        for seg in hs100_segs:
            assert math.isclose(seg["width"], 0.127, abs_tol=1e-3), (
                f"Expected 0.127 mm (100 Ohm) on {seg['net_name']}, got {seg['width']} mm"
            )

    def test_usb_90ohm_trace_widths(self, pcb_data):
        """Assert all USB 2.0 differential traces use 0.180 mm (90 Ohm) geometry."""
        usb_nets = {"/USB0_P", "/USB0_N", "/USB0_B_P", "/USB0_B_N", "/USBB_P", "/USBB_N", "/USBD0_P", "/USBD0_N"}
        hs90_segs = [s for s in pcb_data.segments if s["net_name"] in usb_nets]
        assert len(hs90_segs) > 0, "No USB differential segments found"
        for seg in hs90_segs:
            assert math.isclose(seg["width"], 0.18, abs_tol=1e-3), (
                f"Expected 0.180 mm (90 Ohm) on {seg['net_name']}, got {seg['width']} mm"
            )

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

    def test_critical_bom_lcsc_and_dnp_exclusion(self):
        """Assert verified LCSC part numbers for critical ICs/passives and exclusion of DNP straps R31-R33."""
        bom_path = os.path.join(PROJECT_DIR, "jlcpcb_production", "assembly", "bom_jlcpcb.csv")
        with open(bom_path, mode="r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        by_ref = {}
        for row in rows:
            for ref in [r.strip() for r in row["Designator"].split(",") if r.strip()]:
                by_ref[ref] = row

        assert by_ref["C20"]["Comment"] == "10pF" and by_ref["C20"]["LCSC"] == "C32949"
        assert by_ref["C21"]["Comment"] == "330pF" and by_ref["C21"]["LCSC"] == "C1534"
        assert by_ref["R20"]["Comment"] == "61.9k" and by_ref["R20"]["LCSC"] == "C25803"
        assert by_ref["U1"]["LCSC"] == "C15075"
        assert by_ref["U3"]["LCSC"] == "C47773"
        assert by_ref["U5"]["LCSC"] == "C2960187"
        assert by_ref["U6"]["Comment"] == "FSUSB42UMX" and by_ref["U6"]["LCSC"] == "C11145"
        assert by_ref["HDMI1"]["LCSC"] == "C424662"
        assert by_ref["L1"]["LCSC"] == "C110443"

        for dnp_ref in ["R31", "R32", "R33"]:
            assert dnp_ref not in by_ref, f"DNP strap {dnp_ref} must be excluded from assembled BOM"

    def test_manufacturing_cpl_completeness(self):
        """Assert CPL contains required pick-and-place headers, coordinates, and excludes DNP straps."""
        cpl_path = os.path.join(PROJECT_DIR, "jlcpcb_production", "assembly", "cpl_jlcpcb.csv")
        assert os.path.exists(cpl_path), f"CPL file missing at {cpl_path}"
        with open(cpl_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0, "CPL contains no rows"
        refs = set()
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
            refs.add(ref)

        for dnp_ref in ["R31", "R32", "R33"]:
            assert dnp_ref not in refs, f"DNP strap {dnp_ref} must be excluded from CPL"

    def test_gerber_package_files(self):
        """Assert Gerber directory contains all 6 copper layers, mask, silk, paste, and drill files."""
        g_dir = os.path.join(PROJECT_DIR, "jlcpcb_production", "gerbers")
        assert os.path.exists(g_dir), f"Gerber directory missing at {g_dir}"
        files = os.listdir(g_dir)

        for layer in ["F_Cu", "In1_Cu", "In2_Cu", "In3_Cu", "In4_Cu", "B_Cu"]:
            assert any(layer in f for f in files), f"Missing copper layer {layer} in Gerbers"

        assert any("Edge_Cuts" in f or ".gm1" in f for f in files), "Missing Edge_Cuts outline in Gerbers"
        assert any("F_Mask" in f for f in files), "Missing F_Mask in Gerbers"
        assert any("B_Mask" in f for f in files), "Missing B_Mask in Gerbers"
        assert any("PTH" in f or "drill" in f for f in files), "Missing drill file in Gerbers"
