# Sampling Rules (Development Draft)

Status: **PROPOSED** — freeze before confirmatory collection (protocol §34).
Aligned with Master Protocol v1.0.

## Passage definition

A passage is the smallest contiguous textual unit capable of expressing one complete proposition or tightly coupled proposition set. Do not assume one verse = one independent observation.

## Inclusion (development)

- Works listed in `corpus/manifests/sources.csv` with analyzable text or synthetic instrument text.
- Philosophical / cosmological / natural-philosophical content for targets and philosophical controls.
- Literary negatives: non-cosmological narrative/poetry for Sanskrit negative controls.
- Modern physics references: authored structural descriptions for instrument validation only.

## Exclusion

- Modern editorial footnotes mentioning quantum physics.
- Unseparated commentary mixed into primary text.
- Exact duplicates (keep first by sorted `passage_id`).
- Copyrighted full text in public release without redistribution rights (metadata/hash only).

## Length

- Prefer 40–220 words after normalization (soft bounds for development).
- Extremely short fragments (<15 words) excluded unless they are complete sūtra-like claims with defined context.

## Sampling procedure (development prototype)

1. Allocate quotas by role/tradition (see `corpus/development/prototype100_balance.csv`).
2. Draw from template banks without optimizing for quantum resemblance.
3. Record `source_hash`, license status, and generation script version.
4. Score with frozen-for-run ontology/backend; write manifest.

## Confirmatory (not yet active)

Will use frozen inclusion rules, power-derived *n*, hashed locked corpus, and no mid-stream target–control peeking.
Present status: **LOCKED**.
