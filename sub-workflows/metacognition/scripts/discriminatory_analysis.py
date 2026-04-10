#!/usr/bin/env python3
"""Discriminatory power analysis of score_matrix.csv"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path("/home/ubuntu/.openclaw/workspace-agi-bench/repo/sub-workflows/metacognition")
df = pd.read_csv(BASE / "results/score_matrix.csv", index_col="benchmark")

models = df.columns.tolist()
print(f"Models ({len(models)}): {models}")
print(f"Benchmarks: {len(df)}\n")

# Convert ERROR to NaN
df = df.replace("ERROR", np.nan).astype(float)

# Per-benchmark stats
stats = pd.DataFrame(index=df.index)
stats["valid_n"] = df.notna().sum(axis=1)
stats["mean"] = df.mean(axis=1)
stats["std"] = df.std(axis=1)
stats["min"] = df.min(axis=1)
stats["max"] = df.max(axis=1)
stats["range"] = stats["max"] - stats["min"]

# Flags
flags = {}
for b in df.index:
    row = df.loc[b].dropna()
    reasons = []
    if len(row) == 0:
        reasons.append("no valid scores")
    else:
        if (row > 0.9).all():
            reasons.append("too easy (all > 0.9)")
        if (row < 0.1).all():
            reasons.append("too hard (all < 0.1)")
        if row.std() < 0.05 and len(row) > 1:
            reasons.append(f"non-discriminatory (std={row.std():.4f})")
    if reasons:
        flags[b] = "; ".join(reasons)

print("=== Flagged Benchmarks ===")
for b, r in flags.items():
    print(f"  {b}: {r}")

# Discrimination index: Claude Opus - Ministral 3B
opus_col = "Claude Opus 4.6"
mini_col = "Ministral 3B"
stats["opus_score"] = df[opus_col]
stats["mini_score"] = df[mini_col]
stats["disc_index"] = df[opus_col] - df[mini_col]

disc = stats[["opus_score", "mini_score", "disc_index"]].dropna().sort_values("disc_index", ascending=False)
print("\n=== Discrimination Index (Claude Opus - Ministral 3B) ===")
for b, row in disc.iterrows():
    print(f"  {b}: {row['disc_index']:.4f} (Opus={row['opus_score']:.4f}, Mini={row['mini_score']:.4f})")

# Build markdown
lines = ["# Discriminatory Power Analysis\n"]
lines.append("## Full Score Matrix\n")
lines.append("| Benchmark | " + " | ".join(models) + " |")
lines.append("| --- | " + " | ".join(["---"] * len(models)) + " |")
raw = pd.read_csv(BASE / "results/score_matrix.csv", index_col="benchmark")
for b in raw.index:
    vals = []
    for m in models:
        v = raw.loc[b, m]
        vals.append(str(v) if v != "ERROR" else "ERROR")
    lines.append(f"| {b} | " + " | ".join(vals) + " |")

lines.append("\n## Per-Benchmark Statistics\n")
lines.append("| Benchmark | N | Mean | Std | Min | Max | Range |")
lines.append("| --- | --- | --- | --- | --- | --- | --- |")
for b in stats.index:
    s = stats.loc[b]
    lines.append(f"| {b} | {s['valid_n']:.0f} | {s['mean']:.4f} | {s['std']:.4f} | {s['min']:.4f} | {s['max']:.4f} | {s['range']:.4f} |")

lines.append("\n## Flagged Benchmarks\n")
if flags:
    lines.append("| Benchmark | Flag |")
    lines.append("| --- | --- |")
    for b, r in flags.items():
        lines.append(f"| {b} | {r} |")
else:
    lines.append("No benchmarks flagged.")

lines.append("\n## Discrimination Ranking (Claude Opus 4.6 − Ministral 3B)\n")
lines.append("| Rank | Benchmark | Opus | Ministral 3B | Δ |")
lines.append("| --- | --- | --- | --- | --- |")
for rank, (b, row) in enumerate(disc.iterrows(), 1):
    lines.append(f"| {rank} | {b} | {row['opus_score']:.4f} | {row['mini_score']:.4f} | {row['disc_index']:+.4f} |")

lines.append("\n## Recommendations\n")
# Generate recommendations based on flags
lines.append("### Benchmarks Needing Fixes\n")
for b, r in flags.items():
    if "too easy" in r:
        lines.append(f"- **{b}**: Ceiling effect — increase difficulty (add distractors, reduce time, add adversarial items)")
    elif "too hard" in r:
        lines.append(f"- **{b}**: Floor effect — simplify or provide scaffolding; verify scoring logic isn't broken")
    elif "non-discriminatory" in r:
        lines.append(f"- **{b}**: Low variance — redesign to include items spanning a wider difficulty range")

lines.append("\n### High-Discrimination Benchmarks (Keep/Expand)\n")
for b, row in disc.head(5).iterrows():
    if row["disc_index"] > 0.1:
        lines.append(f"- **{b}** (Δ={row['disc_index']:+.4f}): Strong discriminator — consider expanding item count")

lines.append("\n### Low/Negative-Discrimination Benchmarks (Investigate)\n")
for b, row in disc.tail(5).iterrows():
    if row["disc_index"] < 0.1:
        lines.append(f"- **{b}** (Δ={row['disc_index']:+.4f}): Weak/reversed discrimination — may measure something other than capability")

md = "\n".join(lines) + "\n"
out = BASE / "results/discriminatory_analysis.md"
out.write_text(md)
print(f"\nWrote {out} ({len(md)} bytes)")
