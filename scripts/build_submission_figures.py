"""Render submission figures from frozen supplied-v1 records, without tuning.

Run from the repository root:
    python scripts/build_submission_figures.py
Optional native-SAR examples require the audited local data/supplied-v1 cache.
The benchmark plots need only the small tracked CSVs. No experiment is rerun.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COLORS = ["#767676", "#A3543A", "#6C7D4D", "#B07828", "#4F7180", "#8096A0"]
LABELS = ["Raw", "Median 5", "Lee 5", "Log-bilateral", "U-Net raw", "U-Net median"]


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/submission/figures")
    parser.add_argument("--data-root", type=Path, default=ROOT / "data/supplied-v1")
    parser.add_argument("--example-id", default="Ghana_103272")
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10, "axes.linewidth": 1.1, "axes.spines.top": False,
        "axes.spines.right": False, "svg.fonttype": "none", "pdf.fonttype": 42,
        "savefig.dpi": 300, "figure.facecolor": "white", "axes.facecolor": "white",
    })
    sources = [ROOT / "reports/supplied_classical-v1/results_real.csv",
               ROOT / "reports/supplied_neural-v1/results_neural.csv",
               ROOT / "reports/supplied_classical-v1/results_synthetic.csv",
               ROOT / "reports/supplied_classical-v1/cleanup_ablation.csv",
               ROOT / "reports/supplied_classical-v1/enl_summary.csv"]
    classical, neural, synthetic, cleanup, enl = map(read_rows, sources)
    rows = classical + neural
    macro_ids = [json.loads(row["macro_patch_ids"]) for row in rows]
    assert all(ids == macro_ids[0] for ids in macro_ids) and len(macro_ids[0]) == 15
    for row in rows:
        tp, fp, fn, tn = (int(row[key]) for key in ("tp", "fp", "fn", "tn"))
        assert tp + fp + fn + tn == 4_940_307
        assert np.isclose(float(row["pooled_iou"]), tp / (tp + fp + fn))
        assert np.isclose(float(row["pooled_f1"]), 2 * tp / (2 * tp + fp + fn))
    values = [float(row["pooled_iou"]) for row in rows]
    fig, ax = plt.subplots(figsize=(7.1, 3.0))
    bars = ax.barh(np.arange(6), values, color=COLORS, height=.60,
                   edgecolor="#272727", linewidth=.55)
    ax.set_yticks(np.arange(6), LABELS)
    ax.invert_yaxis()
    ax.set_xlim(0, .51)
    ax.set_xlabel("Pooled water IoU (higher is better)")
    ax.axhline(3.5, color="#aaa", linewidth=.8, linestyle=(0, (3, 3)))
    for bar, value in zip(bars, values):
        ax.text(value + .007, bar.get_y() + bar.get_height()/2, f"{value:.4f}", va="center", fontsize=9)
    ax.grid(axis="x", color="#e5e5e5", linewidth=.65)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=1)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(out / f"water_iou.{ext}", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(4.8, 2.7))
    x = np.arange(4)
    for j, looks in enumerate((1, 4)):
        subset = [row for row in synthetic if int(row["looks"]) == looks]
        assert [r["method"] for r in subset] == ["raw", "median", "lee", "log_bilateral"]
        vals = [float(row["mean_psnr_db"]) for row in subset]
        ax.bar(x + (j - .5)*.36, vals, .34, label=f"L = {looks}",
               color=["#4F7180", "#A3543A"][j], edgecolor="#272727", linewidth=.5,
               hatch=["", "//"][j])
    ax.set_xticks(x, ["Raw", "Median 5", "Lee 7", "Log-bilateral"])
    ax.set_ylabel("Known-reference PSNR (dB)")
    ax.set_ylim(0, 26)
    ax.legend(frameon=False, ncols=2, loc="upper left")
    ax.grid(axis="y", color="#e5e5e5", linewidth=.65)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=1)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(out / f"synthetic_psnr.{ext}", bbox_inches="tight")
    plt.close(fig)

    summary = {"profile": "supplied-first100", "figure_only_no_retuning": True,
               "scored_pixels": 4940307, "macro_water_patches": 15, "dry_patches": 15,
               "no_score_patches": 1, "labels": LABELS,
               "classical": classical, "neural": neural, "synthetic": synthetic,
               "cleanup": cleanup, "enl": enl,
               "median_iou_change": values[1]-values[0],
               "unet_median_iou_change": values[5]-values[4],
               "median_dry_fp_reduction_percent": 100*(1-int(classical[1]["dry_false_positive_pixels"])/int(classical[0]["dry_false_positive_pixels"])),
               "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    example = args.data_root / f"{args.example_id}_S1Hand.tif"
    if example.exists():
        import rasterio
        from sar_water.data import adapt_arrays
        from sar_water.filters import filter_power
        label_path = args.data_root / f"{args.example_id}_LabelHand.tif"
        with rasterio.open(example) as ds:
            image, mask = ds.read(), ds.read_masks() > 0
        with rasterio.open(label_path) as ds:
            labels, label_mask = ds.read(1), ds.read_masks(1) > 0
        patch = adapt_arrays(image, labels, units="db", band_order="VV,VH", input_mask=mask, label_mask=label_mask)
        filtered = filter_power(patch.power, patch.input_valid, method="median", window=5)
        valid = patch.input_valid & patch.label_valid
        raw_mask = (10*np.log10(patch.power[1]) < -20).astype(float)
        filtered_mask = (10*np.log10(filtered[1]) < -20).astype(float)
        truth = labels.astype(float)
        for array in (raw_mask, filtered_mask, truth):
            array[~valid] = np.nan
        cmap = ListedColormap(["#ECE7DC", "#4F7180"])
        cmap.set_bad("#BFB7A6")
        gray = plt.get_cmap("gray").copy(); gray.set_bad("#BFB7A6")
        panels = [image[1], 10*np.log10(filtered[1]), truth, raw_mask, filtered_mask]
        names = ["Raw VH (dB)", "Median 5 VH (dB)", "Manual water label", "Raw threshold", "Median threshold"]
        fig, axes = plt.subplots(1, 5, figsize=(10, 2.15))
        for i, (ax, panel, name) in enumerate(zip(axes, panels, names)):
            ax.imshow(panel, cmap=gray if i < 2 else cmap, vmin=-30 if i < 2 else 0, vmax=0 if i < 2 else 1, interpolation="nearest")
            ax.set_title(name, fontsize=9); ax.axis("off")
            # Full native extent is retained in every saved panel.
            plt.imsave(out / f"example_{i+1}.png", panel, cmap=gray if i<2 else cmap,
                       vmin=-30 if i<2 else 0, vmax=0 if i<2 else 1)
        fig.tight_layout(pad=.3, w_pad=.5)
        for ext in ("png", "pdf", "svg"):
            fig.savefig(out / f"sar_example.{ext}", bbox_inches="tight")
        plt.close(fig)
        summary["example"] = {"patch_id": args.example_id, "disclosure": "illustrative held-out patch, previously used in development training; not a representative-sampling claim", "sar_limits_db": [-30, 0], "mask_colors": {"land": "#ECE7DC", "water": "#4F7180", "invalid": "#BFB7A6"}}
    metadata = ROOT / "reports/submission-v1/figure_data.json"
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(f"Verified all six pooled metrics and fixed macro membership. Figures: {out}")


if __name__ == "__main__":
    main()
