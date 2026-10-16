import re, math, sys, uuid

def generate_uuid():
    return str(uuid.uuid4())

# Load schematic
with open("CM5-AI-Cam-CopperPilot.kicad_sch.orig") as f:
    text = f.read()

# Parse lib_symbols
lib_sym_start = text.find("(lib_symbols")
depth = 0
lib_sym_end = -1
for i in range(lib_sym_start, len(text)):
    if text[i] == '(': depth += 1
    elif text[i] == ')':
        depth -= 1
        if depth == 0:
            lib_sym_end = i + 1
            break
header = text[:lib_sym_start]
lib_symbols = text[lib_sym_start:lib_sym_end]

# Extract pin definitions for each lib symbol
lib_pins = {}
for m in re.finditer(r'\(symbol\s+"([^"]+)"', lib_symbols):
    sym_name = m.group(1)
    s_idx = m.start()
    d = 0
    end = -1
    for j in range(s_idx, len(lib_symbols)):
        if lib_symbols[j] == '(': d += 1
        elif lib_symbols[j] == ')':
            d -= 1
            if d == 0:
                end = j + 1
                break
    sub = lib_symbols[s_idx:end]
    pin_starts = [p.start() for p in re.finditer(r'\(pin\s+\w+\s+\w+', sub)]
    for p_idx in pin_starts:
        pd = 0
        p_end = -1
        for k in range(p_idx, len(sub)):
            if sub[k] == '(': pd += 1
            elif sub[k] == ')':
                pd -= 1
                if pd == 0:
                    p_end = k + 1
                    break
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

print(f"Loaded pin data for {len(lib_pins)} symbol units.")
