#!/usr/bin/env python3
import sys
import os
import json
from PIL import Image, ImageDraw

def crop_issue(issue_id):
    issues_path = "review/issues.json"
    if not os.path.exists(issues_path):
        print(f"Error: {issues_path} not found")
        sys.exit(1)
        
    with open(issues_path) as f:
        issues = json.load(f)
        
    target = None
    for item in issues:
        if item.get("id") == issue_id:
            target = item
            break
            
    if not target:
        print(f"Error: Issue {issue_id} not found in {issues_path}")
        sys.exit(1)
        
    reg = target.get("region", {})
    target_plane = reg.get("sheet") or reg.get("layer", "F.Cu")
    x_min = float(reg.get("x_min", 0))
    y_min = float(reg.get("y_min", 0))
    x_max = float(reg.get("x_max", 0))
    y_max = float(reg.get("y_max", 0))
    
    # 2mm margin
    margin = 2.0
    x_min_m = max(0.0, x_min - margin)
    y_min_m = max(0.0, y_min - margin)
    x_max_m = x_max + margin
    y_max_m = y_max + margin
    
    dpi = 300.0
    scale = dpi / 25.4
    
    px_min_x = int(x_min_m * scale)
    px_min_y = int(y_min_m * scale)
    px_max_x = int(x_max_m * scale)
    px_max_y = int(y_max_m * scale)
    
    box_min_x = int(x_min * scale) - px_min_x
    box_min_y = int(y_min * scale) - px_min_y
    box_max_x = int(x_max * scale) - px_min_x
    box_max_y = int(y_max * scale) - px_min_y
    
    is_sch = "sheet" in reg or "sch" in target_plane.lower()
    if is_sch:
        before_file = "review/renders/baseline/sch_sheet_1.png"
        after_file = "review/renders/final/sch_sheet_1.png"
        if not os.path.exists(after_file):
            after_file = "review/renders/baseline/sch_sheet_1.png"
    else:
        before_file = f"review/renders/baseline/pcb_{target_plane}.png"
        after_file = f"review/renders/final/pcb_{target_plane}.png"
        if not os.path.exists(after_file):
            after_file = before_file
            
    out_dir = f"review/renders/issues/{issue_id}"
    os.makedirs(out_dir, exist_ok=True)
    
    # Crop before
    if os.path.exists(before_file):
        im_b = Image.open(before_file)
        crop_b = im_b.crop((px_min_x, px_min_y, px_max_x, px_max_y))
        draw_b = ImageDraw.Draw(crop_b)
        draw_b.rectangle([box_min_x, box_min_y, box_max_x, box_max_y], outline="red", width=3)
        draw_b.text((box_min_x + 5, max(0, box_min_y - 15)), f"{issue_id} (Before)", fill="red")
        crop_b.save(os.path.join(out_dir, "before.png"))
        
    # Crop after
    if os.path.exists(after_file):
        im_a = Image.open(after_file)
        crop_a = im_a.crop((px_min_x, px_min_y, px_max_x, px_max_y))
        draw_a = ImageDraw.Draw(crop_a)
        draw_a.rectangle([box_min_x, box_min_y, box_max_x, box_max_y], outline="green", width=3)
        draw_a.text((box_min_x + 5, max(0, box_min_y - 15)), f"{issue_id} (After)", fill="green")
        crop_a.save(os.path.join(out_dir, "after.png"))
        
    # Generate crop diff
    if os.path.exists(before_file) and os.path.exists(after_file):
        diff_im = Image.new("RGBA", crop_a.size, (240, 240, 240, 255))
        # Simple pixel diff
        import numpy as np
        arr_b = np.array(crop_b.convert("RGB"), dtype=np.int16)
        arr_a = np.array(crop_a.convert("RGB"), dtype=np.int16)
        diff = np.abs(arr_a - arr_b)
        mask = np.any(diff > 30, axis=2)
        out_arr = np.array(crop_a.convert("RGBA"))
        # Highlight changes: red for removed, green for added
        for y in range(mask.shape[0]):
            for x in range(mask.shape[1]):
                if mask[y, x]:
                    out_arr[y, x] = [255, 0, 0, 255]
        diff_im = Image.fromarray(out_arr)
        draw_d = ImageDraw.Draw(diff_im)
        draw_d.rectangle([box_min_x, box_min_y, box_max_x, box_max_y], outline="blue", width=3)
        draw_d.text((box_min_x + 5, max(0, box_min_y - 15)), f"{issue_id} (Diff)", fill="blue")
        diff_im.save(os.path.join(out_dir, "diff.png"))
        
    print(f"Generated issue crops for {issue_id} in {out_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: crop_issue.py <ISSUE_ID>")
        sys.exit(1)
    crop_issue(sys.argv[1])
