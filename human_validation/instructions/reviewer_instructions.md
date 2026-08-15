# Human Annotation Instructions (RISHI-Q)

Status: REQUIRES_EXTERNAL_HUMAN_VALIDATION

You are labeling structural features, not judging whether a text is "quantum."

## Labels
- 1 = explicitly supported by the passage
- 0 = explicitly contradicted
- NA = not specified / insufficient evidence
- U = ambiguous (use sparingly)

## Hard rules
- "Everything is one" does NOT imply nonseparability/entanglement.
- Interconnected ≠ nonlocal.
- Vibration ≠ QFT.
- Prefer NA over 1 when unsure.
- Every 1 requires an exact evidence span copied from the passage.

## Do not
- Use tradition names or book titles as evidence.
- Upgrade metaphors to physical claims.
- Discuss whether the overall project hypothesis is true while labeling.
