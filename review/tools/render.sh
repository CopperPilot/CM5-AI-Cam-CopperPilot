#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [ "$1" = "--issue" ]; then
    if [ -z "$2" ]; then
        echo "Error: Missing issue ID"
        exit 1
    fi
    python3 "${SCRIPT_DIR}/crop_issue.py" "$2"
    exit 0
fi

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <git-ref|working> <out-dir>"
    echo "       $0 --issue <ISSUE_ID>"
    exit 1
fi

GIT_REF="$1"
OUT_DIR="$2"

mkdir -p "${OUT_DIR}"
ABSOLUTE_OUT="$(cd "${OUT_DIR}" && pwd)"

WORK_DIR=""
if [ "$GIT_REF" = "working" ] || [ "$GIT_REF" = "." ] || [ "$GIT_REF" = "current" ]; then
    WORK_DIR="${PROJECT_ROOT}"
else
    WORK_DIR="$(mktemp -d /tmp/kicad_render_XXXXXX)"
    echo "Exporting git-ref ${GIT_REF} to temporary directory ${WORK_DIR}..."
    git archive "${GIT_REF}" | tar -x -C "${WORK_DIR}"
    # Copy project local 3D shapes/models if present
    if [ -d "${PROJECT_ROOT}/CM5.3dshapes" ]; then
        cp -r "${PROJECT_ROOT}/CM5.3dshapes" "${WORK_DIR}/"
    fi
    if [ -d "${PROJECT_ROOT}/3dmodels" ]; then
        cp -r "${PROJECT_ROOT}/3dmodels" "${WORK_DIR}/"
    fi
fi

cd "${WORK_DIR}"

PCB_FILE="CM5-AI-Cam-CopperPilot.kicad_pcb"
SCH_FILE="CM5-AI-Cam-CopperPilot.kicad_sch"

echo "Rendering Schematic for ${GIT_REF}..."
kicad-cli sch export pdf -o "${ABSOLUTE_OUT}/schematic.pdf" "${SCH_FILE}"
pdftoppm -png -r 300 "${ABSOLUTE_OUT}/schematic.pdf" "${ABSOLUTE_OUT}/sch_page"
if [ -f "${ABSOLUTE_OUT}/sch_page-1.png" ]; then
    mv "${ABSOLUTE_OUT}/sch_page-1.png" "${ABSOLUTE_OUT}/sch_sheet_1.png"
fi

echo "Rendering PCB Layers for ${GIT_REF}..."
LAYERS=("F.Cu" "In1.Cu" "In2.Cu" "In3.Cu" "In4.Cu" "B.Cu" "F.Mask" "B.Mask" "F.SilkS" "B.SilkS" "F.Paste" "B.Paste" "Edge.Cuts" "F.CrtYd" "B.CrtYd" "F.Fab" "B.Fab")

for LAYER in "${LAYERS[@]}"; do
    echo "  Layer: ${LAYER}"
    kicad-cli pcb export pdf --cl Edge.Cuts -l "${LAYER}" --mode-single -o "${ABSOLUTE_OUT}/layer_${LAYER}.pdf" "${PCB_FILE}"
    pdftoppm -png -r 300 "${ABSOLUTE_OUT}/layer_${LAYER}.pdf" "${ABSOLUTE_OUT}/tmp_${LAYER}"
    mv "${ABSOLUTE_OUT}/tmp_${LAYER}-1.png" "${ABSOLUTE_OUT}/pcb_${LAYER}.png"
    rm -f "${ABSOLUTE_OUT}/layer_${LAYER}.pdf"
done

echo "Rendering 3D views for ${GIT_REF}..."
kicad-cli pcb render --side top -w 1600 -h 1200 -o "${ABSOLUTE_OUT}/3d_top.png" "${PCB_FILE}"
kicad-cli pcb render --side bottom -w 1600 -h 1200 -o "${ABSOLUTE_OUT}/3d_bottom.png" "${PCB_FILE}"
kicad-cli pcb render --rotate -45,0,45 -w 1600 -h 1200 -o "${ABSOLUTE_OUT}/3d_iso.png" "${PCB_FILE}"

if [ "$GIT_REF" != "working" ] && [ "$GIT_REF" != "." ] && [ "$GIT_REF" != "current" ]; then
    rm -rf "${WORK_DIR}"
fi

echo "All renders completed successfully in ${ABSOLUTE_OUT}"
