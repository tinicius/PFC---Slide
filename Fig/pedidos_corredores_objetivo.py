"""Figura da última célula de pfc2/notebooks/resultados/novas_msc_b12_b13.ipynb
(unidades coletadas, corredores visitados e f em B/0012 e B/0013), sem o OrderBased e com as cores
padrão por algoritmo das figuras do TCC (figuras_texto_tcc.ipynb).

Uso: pfc2/.venv/bin/python Slide/Fig/pedidos_corredores_objetivo.py <raiz do pfc2>
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

ALGOS_MAP = {
    "aisle_based": "AisleBased",
    "ils_vnd_all": "ILS-VND",
    "andre_feijo_all": "Santos e Baldotto (2025)",
}
ALGOS_ORDEM = list(ALGOS_MAP.values())
ROTULOS_X = ["AisleBased", "ILS-VND", "Santos e\nBaldotto (2025)"]
COR = {
    "AisleBased": "#1f77b4",
    "ILS-VND": "#d62728",
    "Santos e Baldotto (2025)": "#2ca02c",
}
INST = {"instance_0012.txt": "B/0012", "instance_0013.txt": "B/0013"}


def vrg(s):
    return str(s).replace(".", ",")


def fmt_milhar(v, casas=0):
    if casas <= 0 or abs(v - round(v)) < 1e-6:
        return f"{int(round(v)):,}".replace(",", ".")
    int_p = int(v)
    dec_p = int(round((v - int_p) * (10 ** casas)))
    return f"{int_p:,}".replace(",", ".") + f",{dec_p:0{casas}d}"


frames = []
for folder, label in ALGOS_MAP.items():
    for inst in INST:
        d = pd.read_csv(RESULTS / folder / "b" / inst.replace(".txt", ".csv"),
                        usecols=["status", "objective", "items", "aisles"])
        d["algo"], d["instance"] = label, inst
        frames.append(d)
df_runs = pd.concat(frames, ignore_index=True)
assert len(df_runs) == 180 and (df_runs["status"] == "feasible").all()

with plt.style.context("default"):
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
                         "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    x = np.arange(len(ALGOS_ORDEM))
    width = 0.4
    for idx_p, (inst_id, rot) in enumerate(INST.items()):
        ax = axes[idx_p]
        sub = df_runs[df_runs["instance"] == inst_id]
        unidades = [sub[sub["algo"] == a]["items"].mean() for a in ALGOS_ORDEM]
        corredores = [sub[sub["algo"] == a]["aisles"].mean() for a in ALGOS_ORDEM]
        objetivos = [sub[sub["algo"] == a]["objective"].mean() for a in ALGOS_ORDEM]
        cores = [COR[a] for a in ALGOS_ORDEM]

        ax_corr = ax.twinx()
        bars_corr = ax_corr.bar(x + width / 2, corredores, width, facecolor="white",
                                edgecolor=cores, hatch="////", linewidth=1.0)
        bars_unid = ax.bar(x - width / 2, unidades, width, color=cores, alpha=0.55,
                           edgecolor="k", linewidth=0.6)

        max_u, max_c = max(unidades), max(corredores)
        ax.set_ylim(0, max_u * 1.25)
        ax_corr.set_ylim(0, max_c * 1.25)
        for bar, c_val in zip(bars_corr, corredores):
            ax_corr.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max_c * 0.012,
                         fmt_milhar(c_val, 0), ha="center", va="bottom", fontsize=9)
        for bar, u_val in zip(bars_unid, unidades):
            casas_u = 1 if abs(u_val - round(u_val)) > 1e-4 else 0
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max_u * 0.012,
                    fmt_milhar(u_val, casas_u), ha="center", va="bottom", fontsize=9)
        for i in range(len(ALGOS_ORDEM)):
            topo = max(unidades[i] / max_u, corredores[i] / max_c) * max_u
            ax.text(x[i], topo + max_u * 0.085, f"f = {vrg(f'{objetivos[i]:.2f}')}",
                    ha="center", va="bottom", fontsize=9.5)

        ax.set_xticks(x)
        ax.set_xticklabels(ROTULOS_X)
        ax.set_ylabel("Média do número de unidades coletadas")
        ax_corr.set_ylabel("Média do número de corredores visitados")
        ax.set_title(f"({chr(97 + idx_p)}) Instância {rot}")
        ax.grid(alpha=0.3, axis="y")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: fmt_milhar(y)))

    handles = [
        mpatches.Patch(facecolor="#7f7f7f", alpha=0.55, edgecolor="k", label="Média de unidades (eixo esquerdo)"),
        mpatches.Patch(facecolor="white", edgecolor="#555555", hatch="////", label="Média de corredores (eixo direito)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=True)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(OUT.with_suffix(f".{ext}"), dpi=300, bbox_inches="tight", facecolor="white")

print(df_runs.groupby(["instance", "algo"])[["items", "aisles", "objective"]].mean().round(2))
