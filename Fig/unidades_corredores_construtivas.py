"""Figura 2 de pfc2/notebooks/experimentos/comparacao_construtivas_final.ipynb,
no padrão visual de pfc2/notebooks/resultados/figuras_texto_tcc.ipynb.

Uso: pfc2/.venv/bin/python Fig/unidades_corredores_construtivas.py <raiz do pfc2>
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
OUT = Path(__file__).with_suffix("")

ALGOS = {"order_based": "OrderBased", "aisle_based": "AisleBased"}
COR = {"OrderBased": "#7f7f7f", "AisleBased": "#1f77b4"}
RNG_SEED = 12345


def fmt_milhar(v):
    return f"{int(round(v)):,}".replace(",", ".")


frames = []
for folder, label in ALGOS.items():
    for ds in "abx":
        for f in sorted((RESULTS / folder / ds).glob("instance_*.csv")):
            d = pd.read_csv(f, usecols=["status", "items", "aisles"])
            assert (d["status"] == "feasible").all(), f
            d["algo"], d["dataset"], d["instance"] = label, ds, f.stem
            frames.append(d)
raw = pd.concat(frames, ignore_index=True)
inst = raw.groupby(["algo", "dataset", "instance"])[["items", "aisles"]].mean().reset_index()
assert len(inst) == 100

with plt.style.context("default"):
    rng = np.random.default_rng(RNG_SEED)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5))
    for ax, (col, titulo, ylabel) in zip(axes, [
        ("items", "(a) Unidades coletadas (escala log)", "Unidades coletadas por instância"),
        ("aisles", "(b) Corredores visitados (escala log)", "Corredores visitados por instância"),
    ]):
        dados, cores, pos, xt = [], [], [], []
        for k, ds in enumerate("abx"):
            p1, p2 = k * 2.6 + 1.0, k * 2.6 + 1.8
            xt.append((p1 + p2) / 2)
            for p, a in [(p1, "OrderBased"), (p2, "AisleBased")]:
                v = inst[(inst.dataset == ds) & (inst.algo == a)][col].values
                dados.append(v); cores.append(COR[a]); pos.append(p)
                ax.scatter(p + rng.uniform(-0.12, 0.12, len(v)), v, s=16, color=COR[a], alpha=0.65, zorder=3)
        bp = ax.boxplot(
            dados, positions=pos, widths=0.55, patch_artist=True, showmeans=True, showfliers=False,
            meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="k", markersize=6),
        )
        for patch, c in zip(bp["boxes"], cores):
            patch.set_facecolor(c)
            patch.set_alpha(0.45)
        ax.set_yscale("log")
        ax.set_xticks(xt)
        ax.set_xticklabels([f"Dataset {d}" for d in "ABX"])
        ax.set_ylabel(ylabel)
        ax.set_title(titulo)
        ax.grid(alpha=0.3, axis="y")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: fmt_milhar(y) if y >= 1 else str(y).replace(".", ",")))
    handles = [mpatches.Patch(facecolor=COR[a], edgecolor="k", alpha=0.55, label=a) for a in ["OrderBased", "AisleBased"]]
    axes[1].legend(handles=handles, loc="lower right", frameon=True)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT.with_suffix(f".{ext}"), dpi=300, bbox_inches="tight", facecolor="white")

print(inst.groupby(["dataset", "algo"])[["items", "aisles"]].median())
