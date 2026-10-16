import re, math, sys, uuid

def get_uuid():
    return str(uuid.uuid4())

# Load baseline netlist
def parse_netlist(path):
    with open(path) as f: text = f.read()
    nets = {}
    net_blocks = re.findall(r'\(net\s+\(code\s+"[^"]*"\)\s+\(name\s+"([^"]*)"\)(.*?)\n\t\t\)', text, re.DOTALL)
    for name, body in net_blocks:
        nodes = re.findall(r'\(node\s+\(ref\s+"([^"]*)"\)\s+\(pin\s+"([^"]*)"\)', body)
        nets[name] = sorted(nodes)
    return nets

baseline_nets = parse_netlist(".copperpilot/tmp/baseline/baseline.net")
pin_to_net = {}
for net_name, nodes in baseline_nets.items():
    if net_name.startswith("unconnected-"): continue
    clean = net_name[1:] if net_name.startswith("/") else net_name
    for ref, pin in nodes:
        pin_to_net[(ref, str(pin))] = clean

# Power flags
pin_to_net[("#FLG01", "1")] = "CM5_5V"
pin_to_net[("#FLG02", "1")] = "PWR_3V3"
pin_to_net[("#FLG09", "1")] = "GPIO_VREF"
pin_to_net[("#FLG010", "1")] = "CAM_FB1_OUT"
pin_to_net[("#FLG011", "1")] = "GND"
pin_to_net[("#PWR01", "1")] = "GND"

# Load original schematic
with open("CM5-AI-Cam-CopperPilot.kicad_sch.orig") as f:
    text = f.read()

lib_sym_start = text.find("(lib_symbols")
d = 0; lib_sym_end = -1
for i in range(lib_sym_start, len(text)):
    if text[i] == '(': d += 1
    elif text[i] == ')':
        d -= 1
        if d == 0: lib_sym_end = i + 1; break

header = text[:lib_sym_start]
lib_symbols = text[lib_sym_start:lib_sym_end]

# Extract pin definitions for each lib symbol
lib_pins = {}
for m in re.finditer(r'\(symbol\s+"([^"]+)"', lib_symbols):
    sym_name = m.group(1)
    s_idx = m.start(); d = 0; end = -1
    for j in range(s_idx, len(lib_symbols)):
        if lib_symbols[j] == '(': d += 1
        elif lib_symbols[j] == ')':
            d -= 1
            if d == 0: end = j + 1; break
    sub = lib_symbols[s_idx:end]
    pin_starts = [p.start() for p in re.finditer(r'\(pin\s+\w+\s+\w+', sub)]
    for p_idx in pin_starts:
        pd = 0; p_end = -1
        for k in range(p_idx, len(sub)):
            if sub[k] == '(': pd += 1
            elif sub[k] == ')':
                pd -= 1
                if pd == 0: p_end = k + 1; break
        p_block = sub[p_idx:p_end]
        at_m = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', p_block)
        len_m = re.search(r'\(length\s+([\d\.\-]+)\)', p_block)
        name_m = re.search(r'\(name\s+"([^"]*)"', p_block)
        num_m = re.search(r'\(number\s+"([^"]*)"', p_block)
        if at_m and len_m and name_m and num_m:
            px, py = float(at_m.group(1)), float(at_m.group(2))
            prot = float(at_m.group(3) or 0)
            plen = float(len_m.group(1))
            pname, pnum = name_m.group(1), num_m.group(1)
            unit_m = re.search(r'_(\d+)_\d+$', sym_name)
            unit = int(unit_m.group(1)) if unit_m else 1
            parent = re.sub(r'_\d+_\d+$', '', sym_name)
            lib_pins.setdefault((parent, unit), {})[pnum] = {
                "x": px, "y": py, "rot": prot, "len": plen, "name": pname
            }

body = text[lib_sym_end:]
sheet_inst_start = body.find("(sheet_instances")
content = body[:sheet_inst_start]
footer = body[sheet_inst_start:]

sym_starts = [m.start() for m in re.finditer(r'\(symbol\s+\(lib_id', content)]
symbols_list = []
for start in sym_starts:
    d = 0; end = -1
    for j in range(start, len(content)):
        if content[j] == '(': d += 1
        elif content[j] == ')':
            d -= 1
            if d == 0: end = j + 1; break
    block = content[start:end]
    lib_id = re.search(r'\(lib_id\s+"([^"]+)"\)', block).group(1)
    at_m = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', block)
    unit_m = re.search(r'\(unit\s+(\d+)\)', block)
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
    val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', block)
    fp_m = re.search(r'\(property\s+"Footprint"\s+"([^"]*)"', block)
    uuid_m = re.search(r'\(uuid\s+"([^"]+)"\)', block)
    
    unit = int(unit_m.group(1)) if unit_m else 1
    ref = ref_m.group(1) if ref_m else "?"
    symbols_list.append({
        "ref": ref, "val": val_m.group(1) if val_m else "?",
        "lib_id": lib_id, "unit": unit,
        "x": float(at_m.group(1)), "y": float(at_m.group(2)), "rot": float(at_m.group(3) or 0),
        "fp": fp_m.group(1) if fp_m else "",
        "uuid": uuid_m.group(1) if uuid_m else get_uuid(),
        "block": block
    })

print(f"Loaded {len(symbols_list)} placed symbols.")

# Non-colliding coordinates
coords = {
    # SECTION 1: BUCK CONVERTER U5 & TYPE-C (X: 205..380, Y: 35..145)
    "Type_C1": (220.98, 76.20),
    "R2": (246.38, 60.96),
    "C11": (256.54, 60.96),
    "R3": (246.38, 93.98),
    
    "C22": (266.70, 66.04),
    "C23": (276.86, 66.04),
    "R19": (266.70, 96.52),
    "U5": (294.64, 76.20),
    "C24": (325.12, 66.04),
    "L7": (342.90, 76.20),
    "R16": (322.58, 96.52),
    "C21": (330.20, 96.52),
    "R20": (358.14, 96.52),
    "R21": (370.84, 96.52),
    "C25": (347.98, 66.04),
    "C26": (360.68, 66.04),
    "C27": (373.38, 66.04),
    
    "#FLG01": (236.22, 48.26),
    "#FLG02": (355.60, 48.26),
    "#FLG011": (274.32, 48.26),
    "#PWR01": (284.48, 48.26),
    
    # SECTION 2: CAMERA LDO REGULATORS U1, U2, U3 (X: 205..380, Y: 155..280)
    "FB1": (226.06, 177.80),
    "C1": (243.84, 177.80),
    "R17": (213.36, 203.20),
    "R15": (233.68, 203.20),
    "U1": (266.70, 180.34),
    "C2": (297.18, 177.80),
    "C3": (281.94, 205.74),
    "#FLG010": (213.36, 162.56),
    
    "C5": (248.92, 220.98),
    "U2": (271.78, 223.52),
    "C9": (304.80, 220.98),
    "C10": (284.48, 246.38),
    
    "C12": (248.92, 261.62),
    "U3": (271.78, 264.16),
    "C15": (304.80, 261.62),
    "C14": (284.48, 287.02),
    
    # SECTION 3: VIDEO OUTPUTS & POWER SWITCHES (X: 205..380, Y: 290..405)
    "R35": (236.22, 317.50),
    "R36": (248.92, 317.50),
    "HDMI1": (256.54, 355.60),
    "U4": (297.18, 325.12),
    "C17": (281.94, 325.12),
    "C18": (312.42, 325.12),
    "R14": (299.72, 350.52),
    "DSI1": (358.14, 345.44),
    "C19": (325.12, 320.04),
    
    # SECTION 4: IMX219 CAMERA INTERFACE & CSI-2 (X: 385..575, Y: 35..215)
    "L1": (406.40, 78.74),
    "L2": (406.40, 104.14),
    "L3": (406.40, 129.54),
    "J1": (462.28, 114.30),
    "C6": (538.48, 66.04),
    "C7": (551.18, 66.04),
    "C8": (563.88, 66.04),
    
    "R4": (497.84, 104.14),
    "Q1": (508.00, 124.46),
    "R5": (518.16, 104.14),
    
    "R7": (530.86, 124.46),
    "Q2": (543.56, 124.46),
    "R8": (556.26, 124.46),
    
    "H5": (568.96, 124.46),
    "#FLG09": (568.96, 96.52),
    
    "X1": (495.30, 187.96),
    "C16": (477.52, 187.96),
    "R10": (515.62, 187.96),
    "C20": (533.40, 187.96),
    
    # SECTION 5: USB 2.0 SWITCHING & HOST INTERFACE (X: 385..575, Y: 225..310)
    "R24": (403.86, 248.92),
    "R22": (419.10, 264.16),
    "R28": (403.86, 281.94),
    "H4": (429.26, 299.72),
    "U6": (452.12, 264.16),
    "C28": (472.44, 238.76),
    "J2": (500.38, 264.16),
    "U8": (538.48, 264.16),
    "C30": (523.24, 264.16),
    "C29": (553.72, 264.16),
    "R34": (566.42, 287.02),
    
    # SECTION 6: STORAGE & USER I/O EXPANSION (X: 385..575, Y: 320..405)
    "TF1": (416.56, 365.76),
    "U7": (416.56, 335.28),
    "C31": (401.32, 335.28),
    "C32": (431.80, 335.28),
    "R30": (388.62, 335.28),
    
    "PI1": (467.36, 365.76),
    
    "H3": (528.32, 325.12),
    "R29": (520.70, 325.12),
    "R31": (533.40, 325.12),
    "R32": (546.10, 325.12),
    "R33": (558.80, 325.12),
    
    "Key1": (513.08, 375.92),
    "R11": (525.78, 375.92),
    
    "L5": (543.56, 375.92),
    "R12": (556.26, 375.92),
    
    "L6": (553.72, 396.24),
    "R13": (568.96, 396.24),
    
    # SECTION 7 & 8: CM5 MEZZANINE CONNECTORS (X: 25..200)
    "C4": (152.40, 60.96),
    "R1": (172.72, 60.96)
}

box_half_h = {
    "U1": 6.35, "U2": 6.35, "U3": 6.35, "U4": 6.35, "U5": 6.35, "U6": 12.7, "U7": 6.35, "U8": 6.35,
    "Type_C1": 19.05, "J1": 38.1, "J2": 7.62, "HDMI1": 25.4, "DSI1": 20.32, "TF1": 17.78, "PI1": 50.8,
    "Module1": 68.58, "X1": 6.35, "Q1": 3.81, "Q2": 3.81, "L1": 5.08, "L2": 5.08, "L3": 5.08
}

new_symbols_text = []
new_wires_text = []
new_labels_text = []
new_no_connects_text = []

for s in symbols_list:
    ref = s["ref"]
    unit = s["unit"]
    
    # Determine new position
    if ref == "Module1":
        new_x, new_y = (80.0100, 139.7000) if unit == 1 else (-59.6900, 311.1500)
    elif ref in coords:
        new_x, new_y = coords[ref]
    else:
        new_x, new_y = s["x"], s["y"]
        
    s_rot = s["rot"]
    bh = box_half_h.get(ref, 3.81)
    
    if ref.startswith("C") or ref.startswith("R") or ref.startswith("L") or ref.startswith("FB"):
        ref_x, ref_y = new_x + 2.032, new_y - 1.27
        val_x, val_y = new_x + 2.032, new_y + 1.27
    elif ref.startswith("#"):
        ref_x, ref_y = new_x, new_y - 2.54
        val_x, val_y = new_x, new_y + 2.54
    else:
        ref_x, ref_y = new_x, new_y - bh - 2.54
        val_x, val_y = new_x, new_y + bh + 2.54
        
    orig_block = s["block"]
    block = re.sub(r'\(at\s+[\d\.\-]+\s+[\d\.\-]+(?:\s+[\d\.\-]+)?\)', f'(at {new_x:.4f} {new_y:.4f} {s_rot:.1f})', orig_block, count=1)
    block = re.sub(
        r'(\(property\s+"Reference"\s+"[^"]+"\s+)\(at\s+[\d\.\-]+\s+[\d\.\-]+\s+[\d\.\-]+\)',
        rf'\1(at {ref_x:.4f} {ref_y:.4f} 0)',
        block
    )
    block = re.sub(
        r'(\(property\s+"Value"\s+"[^"]+"\s+)\(at\s+[\d\.\-]+\s+[\d\.\-]+\s+[\d\.\-]+\)',
        rf'\1(at {val_x:.4f} {val_y:.4f} 0)',
        block
    )
    new_symbols_text.append(block)
    
    if "ComputeModule5" in s["lib_id"]:
        pins = lib_pins.get(("ComputeModule5-CM5", unit))
    else:
        lib_key = (s["lib_id"], unit)
        alt_lib_key = (s["lib_id"].replace("CM5:", ""), unit)
        pins = lib_pins.get(lib_key) or lib_pins.get(alt_lib_key)
        if not pins:
            pins = lib_pins.get((s["lib_id"], 1)) or lib_pins.get((s["lib_id"].replace("CM5:", ""), 1))
        
    if pins:
        sorted_pins = sorted(pins.items(), key=lambda p: (int(p[0]) if p[0].isdigit() else 999, p[0]))
        # Track pin coordinates to deduplicate coincident pins (e.g. Type-C GND and VBUS pins)
        seen_pin_coords = set()
        for idx, (pnum, pinfo) in enumerate(sorted_pins):
            px, py, prot = pinfo["x"], pinfo["y"], pinfo["rot"]
            pin_sheet_x = round(new_x + px, 4)
            pin_sheet_y = round(new_y - py, 4)
            
            coord_key = (pin_sheet_x, pin_sheet_y)
            if coord_key in seen_pin_coords:
                # Coincident pin (e.g. Type_C1 A1/A12/B1/B12 or A4/A9/B4/B9)
                # Skip duplicate wire and label since they share the same physical pin terminal
                continue
            seen_pin_coords.add(coord_key)
            
            net = pin_to_net.get((ref, pnum))
            if net:
                is_dense = ref in ["Module1", "PI1", "J1", "HDMI1", "DSI1"]
                if is_dense:
                    stub_len = 5.08 if (idx % 2 == 0) else 10.16
                else:
                    stub_len = 5.08
                    
                if prot == 0:
                    wire_end_x = pin_sheet_x - stub_len
                    wire_end_y = pin_sheet_y
                    l_rot = 0
                    l_just = "right"
                elif prot == 180:
                    wire_end_x = pin_sheet_x + stub_len
                    wire_end_y = pin_sheet_y
                    l_rot = 0
                    l_just = "left"
                elif prot == 270: # Top pin -> wire goes UP (-Y)
                    wire_end_x = pin_sheet_x
                    wire_end_y = pin_sheet_y - stub_len
                    l_rot = 90
                    l_just = "left"
                elif prot == 90: # Bottom pin -> wire goes DOWN (+Y)
                    wire_end_x = pin_sheet_x
                    wire_end_y = pin_sheet_y + stub_len
                    l_rot = 90
                    l_just = "right"
                else:
                    wire_end_x = pin_sheet_x + stub_len
                    wire_end_y = pin_sheet_y
                    l_rot = 0
                    l_just = "left"
                    
                wire_str = f'\t(wire (pts (xy {pin_sheet_x:.4f} {pin_sheet_y:.4f}) (xy {wire_end_x:.4f} {wire_end_y:.4f})) (stroke (width 0) (type solid)) (uuid "{get_uuid()}"))'
                label_str = f'\t(label "{net}" (at {wire_end_x:.4f} {wire_end_y:.4f} {l_rot}) (effects (font (size 1.27 1.27)) (justify {l_just})) (uuid "{get_uuid()}"))'
                new_wires_text.append(wire_str)
                new_labels_text.append(label_str)
            else:
                nc_str = f'\t(no_connect (at {pin_sheet_x:.4f} {pin_sheet_y:.4f}) (uuid "{get_uuid()}"))'
                new_no_connects_text.append(nc_str)

frames = [
    ("SECTION 1: 5V TO 3.3V BUCK REGULATOR (MP1658)", (205.74, 35.56), (380.00, 147.32)),
    ("SECTION 2: CAMERA LDO REGULATORS (2.8V, 1.8V, 1.2V)", (205.74, 154.94), (380.00, 281.94)),
    ("SECTION 3: VIDEO OUTPUTS & POWER SWITCHES", (205.74, 289.56), (380.00, 403.86)),
    ("SECTION 4: IMX219 CAMERA INTERFACE & MIPI CSI-2", (386.08, 35.56), (571.50, 218.44)),
    ("SECTION 5: USB 2.0 SWITCHING & HOST INTERFACE", (386.08, 226.06), (571.50, 312.42)),
    ("SECTION 6: STORAGE & USER I/O EXPANSION", (386.08, 320.04), (571.50, 403.86)),
    ("SECTION 7: CM5 MEZZANINE 1 (POWER & LOW-SPEED I/O)", (25.40, 35.56), (198.12, 218.44)),
    ("SECTION 8: CM5 MEZZANINE 2 (HIGH-SPEED SERIAL I/O)", (25.40, 226.06), (198.12, 403.86))
]

decorations = []
for title, (x1, y1), (x2, y2) in frames:
    rect_str = f'\t(rectangle (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (stroke (width 0.254) (type dash)) (fill (type none)) (uuid "{get_uuid()}"))'
    tx, ty = x1 + 3.81, y1 + 5.08
    text_str = f'\t(text "{title}" (at {tx:.4f} {ty:.4f} 0) (effects (font (size 2.0 2.0) (bold yes)) (justify left)) (uuid "{get_uuid()}"))'
    decorations.append(rect_str)
    decorations.append(text_str)

full_content = "\n".join(decorations) + "\n" + "\n".join(new_symbols_text) + "\n" + "\n".join(new_wires_text) + "\n" + "\n".join(new_labels_text) + "\n" + "\n".join(new_no_connects_text) + "\n"
full_schematic = header + lib_symbols + "\n" + full_content + footer

with open("CM5-AI-Cam-CopperPilot.kicad_sch", "w") as f:
    f.write(full_schematic)

print(f"Generated clean schematic: {len(new_symbols_text)} symbols, {len(new_wires_text)} wires, {len(new_labels_text)} labels, {len(new_no_connects_text)} no-connects.")
