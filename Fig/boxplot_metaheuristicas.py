"""Figura 8 do texto (boxplot_metaheuristicas), mesmo código de
pfc2/notebooks/resultados/figuras_texto_tcc.ipynb, com rótulos "Dataset A/B/X".

Uso: pfc2/.venv/bin/python Slide/Fig/boxplot_metaheuristicas.py <raiz do pfc2>
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(sys.argv[1])
RESULTS = ROOT / "project" / "results"
BEST_CSV = ROOT / "best_solutions" / "best_objectives.csv"
OUT = Path(__file__).with_suffix("")

ALGOS = {"ils_vnd_all": "ILS-VND", "andre_feijo_all": "Santos e Baldotto (2025)"}
COR = {"ILS-VND": "#d62728", "Santos e Baldotto (2025)": "#2ca02c"}
RNG_SEED = 12345


def vrg(s):
    return str(s).replace(".", ",")


frames = []
for folder, label in ALGOS.items():
    for ds in "abx":
        for f in sorted((RESULTS / folder / ds).glob("instance_*.csv")):
            d = pd.read_csv(f, usecols=["status", "objective"])
            d["algo"], d["dataset"], d["instance"] = label, ds, f.stem + ".txt"
            frames.append(d)
raw = pd.concat(frames, ignore_index=True)
best = pd.read_csv(BEST_CSV).rename(columns={"best_objective": "best"})
raw = raw.merge(best, on=["dataset", "instance"], how="left")
assert (raw["status"] == "feasible").all() and raw["best"].notna().all()
raw["rpd"] = (raw["best"] - raw["objective"]) / raw["best"] * 100.0
agg = raw.groupby(["dataset", "instance", "algo"], as_index=False).agg(rpd=("rpd", "mean"), n=("rpd", "size"))
assert (agg["n"] == 30).all() and len(agg) == 100
RPD = agg.pivot(index=["dataset", "instance"], columns="algo", values="rpd")
ds_idx = RPD.index.get_level_values("dataset")

with plt.style.context("default"):
    rng_j = np.random.default_rng(RNG_SEED)
    fig, ax = plt.subplots(figsize=(7.8, 4.5))
    dados, cores, xpos, xlab = [], [], [], []
    for k, d in enumerate("abx"):
        sel = ds_idx == d
        p1, p2 = k * 2.6 + 1.0, k * 2.6 + 1.8
        xpos.append((p1 + p2) / 2.0)
        xlab.append(f"Dataset {d.upper()}")
        for p, a in [(p1, "ILS-VND"), (p2, "Santos e Baldotto (2025)")]:
            vals = RPD.loc[sel, a].values
            dados.append(vals); cores.append(COR[a])
            ax.scatter(p + rng_j.uniform(-0.12, 0.12, len(vals)), vals, s=16, color=COR[a], alpha=0.65, zorder=3)
    positions = [k * 2.6 + o for k in range(3) for o in (1.0, 1.8)]
    bp = ax.boxplot(
        dados, positions=positions, widths=0.55, patch_artist=True, showmeans=True, showfliers=False,
        meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="k", markersize=6),
    )
    for patch, c in zip(bp["boxes"], cores):
        patch.set_facecolor(c)
        patch.set_alpha(0.45)
    ax.axhline(0, color="k", lw=0.8, ls="--", alpha=0.6)
    ax.set_xticks(xpos)
    ax.set_xticklabels(xlab)
    ax.set_ylabel("RPD médio por instância (%)")
    ax.grid(alpha=0.3, axis="y")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: vrg(f"{y:.1f}")))
    handles = [mpatches.Patch(facecolor=COR[a], edgecolor="k", alpha=0.55, label=a) for a in COR]
    ax.legend(handles=handles, loc="upper left", frameon=True)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT.with_suffix(f".{ext}"), dpi=300, bbox_inches="tight", facecolor="white")

print(RPD.groupby(level="dataset").agg(["mean", "median"]).round(3))
