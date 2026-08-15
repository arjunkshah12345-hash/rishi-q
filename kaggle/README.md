# Kaggle workflow (RISHI-Q)

## Why Kaggle is required to settle H1

Local heuristic annotation floors out on literary historical English. GPU open-model annotation is the next instrument stage.

## Bundle

```bash
uv run python scripts/prepare_kaggle_bundle.py
```

Upload **`kaggle/rishiq_kaggle_bundle_public.zip`** as a Kaggle dataset (do not publish `blinding_map.PRIVATE.json`).

## Run

1. New Kaggle Notebook → GPU
2. Add the dataset
3. Copy/open `annotation.ipynb`
4. Run all cells
5. Download `annotations.parquet` + `manifest.json`

## Join on Mac

```bash
uv run python scripts/join_kaggle_annotations.py \
  --annotations ~/Downloads/annotations.parquet \
  --blinding-map kaggle/bundle/blinding_map.PRIVATE.json
```

Then inspect `results/exploratory/kaggle_joined/primary_effect.json`.

Still **not** confirmatory until preregistration + human validation.
