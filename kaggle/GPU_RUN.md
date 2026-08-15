# Kaggle annotation run — status

**Account:** `aks1321`  
**Dataset:** https://www.kaggle.com/datasets/aks1321/rishiq-kaggle-bundle-public  

| Kernel | URL | Role |
|--------|-----|------|
| CPU pilot (active) | https://www.kaggle.com/code/aks1321/rishi-q-cpu-annotation-pd-pilot | Working path while GPU blocked |
| GPU pilot | https://www.kaggle.com/code/aks1321/rishi-q-gpu-annotation-pd-pilot | Same code; needs real GPU |
| GPU diag | https://www.kaggle.com/code/aks1321/rishi-q-gpu-diag | Confirmed no `/dev/nvidia*` |

## Blocker: no GPU on batch workers

Diag (T4 and P100): `nvidia-smi` missing, `torch 2.10.0+cpu`. Metadata `enable_gpu` / `--accelerator` alone is not enough for this account.

**You need to (on aks1321):**

1. https://www.kaggle.com/settings — verify phone if prompted  
2. Open the GPU notebook → Accelerator → **GPU T4** → Save & Run All  
3. Confirm logs show a Tesla device

## What is running now

**CPU kernel v2** (no GPU request):

- Bundle + model mounts work under new layout:
  - `/kaggle/input/datasets/aks1321/rishiq-kaggle-bundle-public`
  - `/kaggle/input/models/qwen-lm/qwen2.5/transformers/0.5b-instruct/1`
- 40 passages · Qwen2.5-0.5B-Instruct · oneshot JSON · exploratory  
- Slow on CPU (large `max_new_tokens`); may take hours

```bash
python3 -m kaggle kernels status aks1321/rishi-q-cpu-annotation-pd-pilot
python3 -m kaggle kernels output aks1321/rishi-q-cpu-annotation-pd-pilot -p results/exploratory/kaggle_gpu
uv run python scripts/join_kaggle_annotations.py \
  --annotations results/exploratory/kaggle_gpu/annotations.parquet \
  --blinding-map kaggle/bundle/blinding_map.PRIVATE.json
```

## Local MPS

`scripts/run_local_mps_annotation.py` is ready, but disk was ~1 GB free (need ~3 GB for 1.5B weights). Free space, then run locally.

## Latest result (CPU kernel v2 — COMPLETE)

- 40 passages · ~35 min · Qwen2.5-0.5B-Instruct on CPU  
- Outputs: `results/exploratory/kaggle_gpu/annotations.parquet`  
- **All 1440 labels NA** — 0.5B cannot reliably emit the full 36-feature JSON oneshot (`missing_or_unparsed` dominant)  
- Join ran: exploratory only; ΔQ null / QS≈0 (no positives)

**Next for usable LLM labels:** enable real GPU on `aks1321` (phone verify + UI Accelerator), then re-run with **1.5B-instruct** (already in GPU kernel `model_sources`), or switch to batched/per-feature prompts.

## Continued experiment (batched v3)

Pushed batched feature labeling (6 features/call, `ann-v0.3-batched6`) to improve over all-NA oneshot.
Default cap raised toward 80 passages on CPU while GPU remains blocked.
