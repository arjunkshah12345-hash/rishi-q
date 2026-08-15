# Annotation model card (RISHI-Q)

## heuristic-annotator v0.1.0

- **Intended use:** Local development, unit tests, instrument positive/negative controls on MacBook Air.
- **Not intended for:** Confirmatory scientific claims about Sanskrit–quantum correspondence.
- **Method:** Deterministic regex/heuristic structural cues aligned to ontology examples.
- **Limitations:** Brittle to paraphrase; English-centric; no Sanskrit morphology; can miss implicit structure; must not be tuned to inflate Sanskrit QS.
- **Logging:** Always record `model_name`, `model_revision`, `prompt_version` in experiment manifests.

## Future open LLM backends (Kaggle)

Document exact Hugging Face model id + revision commit hash. Never bury prompts only in notebooks.
