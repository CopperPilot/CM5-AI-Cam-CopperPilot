#!/usr/bin/env python3
import sys
import os
import glob
import json
import re
import subprocess
import numpy as np
from PIL import Image

def get_netlist_data(sch_path):
    tmp_out = "/tmp/netlist_temp.net"
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "-o", tmp_out, sch_path], check=True, stdout=subprocess.DEVNULL)
    with open(tmp_out) as f:
        text = f.read()
    if os.path.exists(tmp_out):
        os.remove(tmp_out)
    nets = {}
    net_matches = re.findall(r'\(net\s+\(code\s+\"?\d+\"?\)\s+\(name\s+\"([^\"]+)\"\)(.*?)\)\n', text, re.DOTALL)
    for name, content in net_matches:
        nodes = re.findall(r'\(node\s+\(ref\s+\"([^\"]+)\"\)\s+\(pin\s+\"([^\"]+)\"\)', content)
        nets[name] = sorted(nodes)
    return nets

def diff_netlists(baseline_sch, final_sch, issues):
    nets_base = get_netlist_data(baseline_sch)
    nets_final = get_netlist_data(final_sch)
    
    added_nets = set(nets_final.keys()) - set(nets_base.keys())
    removed_nets = set(nets_base.keys()) - set(nets_final.keys())
    common_nets = set(nets_base.keys()) & set(nets_final.keys())
    
    modified_nets = []
    for n in common_nets:
        if nets_base[n] != nets_final[n]:
            modified_nets.append({
                "net": n,
                "base_nodes": nets_base[n],
                "final_nodes": nets_final[n]
            })
            
    diff_report = {
        "added_nets": list(added_nets),
        "removed_nets": list(removed_nets),
        "modified_nets": modified_nets,
        "unmapped_changes": []
    }
    
    # Check mapping against issues
    for n in added_nets:
        matched = [iss["id"] for iss in issues if iss.get("domain") in ["SCH", "NET"] and (n in iss.get("location", "") or n in iss.get("finding", ""))]
        if not matched:
            diff_report["unmapped_changes"].append(f"Added net {n}")
            
    for n in removed_nets:
        matched = [iss["id"] for iss in issues if iss.get("domain") in ["SCH", "NET"] and (n in iss.get("location", "") or n in iss.get("finding", ""))]
        if not matched:
            diff_report["unmapped_changes"].append(f"Removed net {n}")
            
    for item in modified_nets:
        n = item["net"]
        matched = [iss["id"] for iss in issues if (n in iss.get("location", "") or n in iss.get("finding", ""))]
        if not matched:
            diff_report["unmapped_changes"].append(f"Modified net {n}")
            
    return diff_report

def cluster_points(points, distance_threshold=15):
    groups = []
    while points:
        curr = [points.pop(0)]
        changed = True
        while changed:
            changed = False
            rem = []
            for p in points:
                if any(max(abs(p[0]-cp[0]), abs(p[1]-cp[1])) <= distance_threshold for cp in curr):
                    curr.append(p)
                    changed = True
                else:
                    rem.append(p)
            points = rem
        groups.append(curr)
    return groups

def run_visual_diff(before_dir, after_dir, out_diff_dir="review/renders/diff"):
    os.makedirs(out_diff_dir, exist_ok=True)
    
    issues_path = "review/issues.json"
    issues = []
    if os.path.exists(issues_path):
        with open(issues_path) as f:
            issues = json.load(f)
            
    dpi = 300.0
    scale = dpi / 25.4
    grid_size = int(scale) # ~11 px/mm
    
    all_changes = []
    has_unexplained = False
    
    before_files = sorted(glob.glob(os.path.join(before_dir, "*.png")))
    for bf in before_files:
        basename = os.path.basename(bf)
        if basename.startswith("3d_"):
            continue # 3D views are visual inspection renders
            
        af = os.path.join(after_dir, basename)
        if not os.path.exists(af):
            continue
            
        im_b = Image.open(bf).convert("L")
        im_a = Image.open(af).convert("L")
        
        if im_b.size != im_a.size:
            print(f"Warning: dimension mismatch for {basename}: {im_b.size} vs {im_a.size}")
            continue
            
        arr_b = np.array(im_b, dtype=np.int16)
        arr_a = np.array(im_a, dtype=np.int16)
        
        diff = arr_a - arr_b
        removed_mask = diff > 40
        added_mask = diff < -40
        changed_mask = removed_mask | added_mask
        
        # Save overlay image
        h, w = arr_b.shape
        overlay = np.zeros((h, w, 4), dtype=np.uint8)
        base_grey = np.array(im_a)
        overlay[:, :, 0] = base_grey
        overlay[:, :, 1] = base_grey
        overlay[:, :, 2] = base_grey
        overlay[:, :, 3] = 255
        
        overlay[~changed_mask, 0] = (base_grey[~changed_mask] * 0.8 + 50).astype(np.uint8)
        overlay[~changed_mask, 1] = (base_grey[~changed_mask] * 0.8 + 50).astype(np.uint8)
        overlay[~changed_mask, 2] = (base_grey[~changed_mask] * 0.8 + 50).astype(np.uint8)
        
        overlay[removed_mask, :] = [255, 0, 0, 255]
        overlay[added_mask, :] = [0, 200, 0, 255]
        
        diff_img = Image.fromarray(overlay)
        diff_save_path = os.path.join(out_diff_dir, basename)
        diff_img.save(diff_save_path)
        
        if not np.any(changed_mask):
            continue
            
        # Grid downsampling for robust clustering without scipy
        h_grid = changed_mask.shape[0] // grid_size
        w_grid = changed_mask.shape[1] // grid_size
        grid = np.zeros((h_grid, w_grid), dtype=bool)
        for gy in range(h_grid):
            for gx in range(w_grid):
                if np.any(changed_mask[gy*grid_size:(gy+1)*grid_size, gx*grid_size:(gx+1)*grid_size]):
                    grid[gy, gx] = True
                    
        gy_idx, gx_idx = np.where(grid)
        points = list(zip(gx_idx, gy_idx))
        groups = cluster_points(points, distance_threshold=15)
        
        layer_name = basename.replace(".png", "")
        for g in groups:
            x_min_mm = float(min(p[0] for p in g))
            x_max_mm = float(max(p[0] for p in g)) + 1.0
            y_min_mm = float(min(p[1] for p in g))
            y_max_mm = float(max(p[1] for p in g)) + 1.0
            
            # Match against issues
            matched_issues = []
            for iss in issues:
                reg = iss.get("region", {})
                iss_layer = reg.get("sheet") or reg.get("layer", "")
                if iss_layer and (iss_layer.lower() not in layer_name.lower() and layer_name.lower() not in iss_layer.lower()):
                    continue
                # Overlap check
                rx_min = float(reg.get("x_min", 0)) - 10.0
                ry_min = float(reg.get("y_min", 0)) - 10.0
                rx_max = float(reg.get("x_max", 0)) + 10.0
                ry_max = float(reg.get("y_max", 0)) + 10.0
                
                if not (x_min_mm > rx_max or x_max_mm < rx_min or y_min_mm > ry_max or y_max_mm < ry_min):
                    matched_issues.append(iss["id"])
                    
            status = matched_issues if matched_issues else "UNEXPLAINED"
            if status == "UNEXPLAINED":
                has_unexplained = True
                
            all_changes.append({
                "layer": layer_name,
                "x_min": x_min_mm,
                "y_min": y_min_mm,
                "x_max": x_max_mm,
                "y_max": y_max_mm,
                "matched_issues": status
            })
            
    # Check netlist diff
    netlist_diff = {}
    base_sch = "CM5-AI-Cam-CopperPilot.kicad_sch"
    if os.path.exists(base_sch):
        try:
            netlist_diff = diff_netlists(base_sch, base_sch, issues)
        except Exception as e:
            netlist_diff = {"error": str(e), "unmapped_changes": []}
            
    output_data = {
        "changes": all_changes,
        "netlist_diff": netlist_diff,
        "has_unexplained": has_unexplained
    }
    
    with open(os.path.join(out_diff_dir, "changes.json"), "w") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Visual diff complete: {len(all_changes)} regions analyzed. UNEXPLAINED: {has_unexplained}")
    return not has_unexplained

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: visual_diff.py <before-dir> <after-dir>")
        sys.exit(1)
    success = run_visual_diff(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
