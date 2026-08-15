# arXiv submission notes — RISHI-Q

## Suggested categories
- primary: `physics.hist-ph` (History and Philosophy of Physics)
- cross-list: `cs.CL` (Computation and Language)

## Build PDF
```bash
cd paper
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

Or:
```bash
make -C paper
```

## Honesty checklist before upload
- [ ] Confirmatory still described as LOCKED
- [ ] Capra autopsy labeled EXPLORATORY
- [ ] No “ancient QM discovered” claims
- [ ] Figures resolve (`paper/figures/`)
- [ ] Blinding maps not included in the upload zip
- [ ] License / data statement accurate

## Upload bundle
Include `main.tex`, `references.bib`, `tables/*.tex`, `figures/*.png` used by the manuscript.
Do **not** upload private blinding maps or `.env` files.
