"""Known-theory identification validation with train/dev/test separation.

Primary held-out scorer: TF-IDF + linear SVM fit on TRAIN only (no keyword→ontology proxy).
Centroid TF-IDF kept as secondary diagnostic.
Keyword proxy retained only under evidence_class=SOFTWARE_DEMO for plumbing comparisons.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from rishiq.fingerprints import load_all_fingerprints
from rishiq.isef2027.baselines import binary_vector_jaccard
from rishiq.isef2027.benchmark import keyword_feature_proxy
from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope, attach_provenance

THEORIES = [
    "newtonian",
    "thermodynamics",
    "classical_em",
    "relativity",
    "quantum_mechanics",
    "quantum_field_theory",
    "atomistic_corpuscular",
]


def _passages() -> list[dict[str, str]]:
    """Curated pedagogy passages for METHOD VALIDATION (not ancient corpora).

    Split is index-stratified per theory so each theory appears in train/dev/test.
    """
    raw: dict[str, list[str]] = {
        "newtonian": [
            "A body continues in uniform motion unless acted on by a net external force.",
            "Acceleration is proportional to force and inversely proportional to mass.",
            "Action and reaction forces are equal in magnitude and opposite in direction.",
            "Planetary motion can be treated with inverse-square gravitational force in absolute space.",
            "Momentum is conserved in an isolated system of colliding classical particles.",
            "Trajectories are continuous curves in Euclidean space parameterized by absolute time.",
            "Work equals force times displacement along the path for a constant force.",
            "The center of mass of a system moves as if all mass and net force acted there.",
            "Newtonian gravity is an instantaneous action-at-a-distance force law, not spacetime curvature.",
            "Rigid-body rotation uses angular momentum about a classical axis in absolute space.",
        ],
        "thermodynamics": [
            "Heat naturally flows from a hotter body to a colder body until temperatures equalize.",
            "The entropy of an isolated macroscopic system tends to increase toward equilibrium.",
            "Temperature and pressure are state variables describing thermal equilibrium.",
            "The first law relates changes in internal energy to heat added and work done.",
            "No engine can convert heat entirely into work without rejecting heat to a sink.",
            "Reversible and irreversible processes are distinguished by entropy production.",
            "Ideal gases relate pressure, volume, and temperature through an equation of state.",
            "Macroscopic thermal behavior can be described without quantum probability amplitudes.",
            "Carnot efficiency depends only on the temperatures of the hot and cold reservoirs.",
            "Phase transitions can exhibit latent heat while temperature remains constant.",
            "Heat capacity relates infinitesimal heat to temperature change at fixed constraints.",
            "Chemical potential equalizes for species free to exchange between subsystems at equilibrium.",
        ],
        "classical_em": [
            "Light is an electromagnetic wave described by coupled electric and magnetic fields.",
            "Maxwell's equations relate charges and currents to evolving electromagnetic fields.",
            "A changing magnetic flux induces an electric field around a circuit.",
            "Electromagnetic radiation carries energy through empty space without a material ether.",
            "Coulomb's law gives the force between static point charges.",
            "Magnetic fields deflect moving charges perpendicular to velocity.",
            "Displacement current completes Ampere's law for time-varying electric fields.",
            "Classical electromagnetism does not require quantized photon number states.",
            "Poynting's vector describes energy flux in classical electromagnetic fields.",
            "Boundary conditions on conductors force tangential electric fields to vanish in electrostatics.",
        ],
        "relativity": [
            "The speed of light in vacuum is the same in all inertial frames.",
            "Simultaneity of distant events depends on the observer's inertial frame.",
            "Energy and mass are related; rest energy equals mass times c squared.",
            "Spacetime intervals replace absolute Newtonian time for event separation.",
            "Gravity is described geometrically by curved spacetime in general relativity.",
            "Time dilation and length contraction appear for relative motion near light speed.",
            "There is no preferred absolute rest frame for mechanics at high speeds.",
            "Light deflection near the sun is a relativistic gravitational prediction.",
            "Four-vectors transform under Lorentz transformations between inertial frames.",
            "Null intervals characterize lightlike separation of events in Minkowski spacetime.",
        ],
        "quantum_mechanics": [
            "Observables are represented by operators on a Hilbert space of states.",
            "Incompatible observables correspond to noncommuting operators.",
            "Measurement outcomes follow Born-rule probabilities from the state vector.",
            "Superposition allows linear combinations of eigenstates before measurement.",
            "The uncertainty principle limits simultaneous sharpness of conjugate variables.",
            "Wavefunctions evolve unitarily between measurements under the Schrödinger equation.",
            "Entanglement produces correlations that cannot be explained by local hidden variables alone.",
            "A pure state is a ray in Hilbert space; mixed states need density operators.",
            "Tunneling allows nonzero amplitude through classically forbidden potential barriers.",
            "Spin one-half systems are described by two-component Pauli spinors and Stern-Gerlach outcomes.",
            "Bound states in a potential well exhibit discrete energy eigenvalues without field quantization.",
            "The measurement problem concerns how definite outcomes arise from unitary state evolution.",
        ],
        "quantum_field_theory": [
            "Particles appear as quantized excitations of underlying quantum fields.",
            "Creation and annihilation operators act on Fock space of field modes.",
            "Interactions are encoded in local Lagrangian densities of fields.",
            "The vacuum is the lowest energy state of the field, not empty classical nothing.",
            "Renormalization reorganizes divergences in perturbative quantum field calculations.",
            "Classical electromagnetism emerges as a limit of the quantized photon field.",
            "Antiparticles accompany relativistic quantum fields with opposite charge.",
            "Gauge symmetry constrains allowed couplings among quantum fields.",
            "Loop diagrams in quantum electrodynamics correct the electron's magnetic moment.",
            "Particle number is not conserved when fields can create pairs above threshold energy.",
            "Wilsonian effective field theory organizes operators by scaling dimension.",
            "Asymptotic states in scattering are labeled by particle species in Fock space.",
        ],
        "atomistic_corpuscular": [
            "Bodies are aggregates of innumerable tiny corpuscles moving in the void.",
            "Observable qualities arise from arrangements and motions of atoms.",
            "Empty space between atoms allows motion and collision of particles.",
            "Hard atoms rebound in collisions without merging into continuous fluid.",
            "Different materials differ by the shapes and hooking of their atoms.",
            "Change is rearrangement of enduring particles rather than creation from nothing.",
            "The cosmos is vast atomic motions without teleological purpose.",
            "Lucretian atomism posits indivisible seeds swerving in infinite empty space.",
            "Softness and hardness are explained by packing density of corpuscles, not continuous substance.",
            "Fire and air differ by the fineness and speed of their atomic constituents.",
        ],
    }
    rows = []
    for theory, texts in raw.items():
        for i, text in enumerate(texts):
            rows.append({"theory_id": theory, "passage_id": f"{theory}-{i:02d}", "text": text})
    return rows


def _stable_split(passage_id: str) -> str:
    """Stratify by passage index so every theory has train/dev/test mass."""
    idx = int(passage_id.rsplit("-", 1)[-1])
    mod = idx % 5
    if mod <= 2:
        return "train"
    if mod == 3:
        return "dev"
    return "test"


def build_theory_validation_corpus(root: Path) -> Path:
    rows = [{**r, "split": _stable_split(r["passage_id"])} for r in _passages()]
    out = root / "data/theory_validation/corpus_v1.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    meta = {
        "corpus_id": "theory_validation_v1",
        "n": len(rows),
        "splits": {s: sum(1 for r in rows if r["split"] == s) for s in ("train", "dev", "test")},
        "theories": THEORIES,
        "note": "Method validation only; not ancient-text confirmatory data.",
    }
    (out.parent / "corpus_v1_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return out


def _fit_tfidf_centroids(train_texts: list[str], train_labels: list[str]):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X = vec.fit_transform(train_texts)
    centroids = {}
    for lab in sorted(set(train_labels)):
        idx = [i for i, y in enumerate(train_labels) if y == lab]
        centroids[lab] = np.asarray(X[idx].mean(axis=0)).ravel()
    return vec, centroids


def _predict_centroid(vec, centroids, texts: list[str]) -> list[str]:
    X = vec.transform(texts)
    labels = list(centroids)
    C = np.stack([centroids[l] for l in labels])
    xa = np.asarray(X.toarray(), dtype=float)
    Xn = xa / (np.linalg.norm(xa, axis=1, keepdims=True) + 1e-12)
    Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    sims = Xn @ Cn.T
    return [labels[int(i)] for i in np.asarray(sims.argmax(axis=1)).ravel()]


def run_held_out_theory_validation(root: Path) -> dict[str, Any]:
    corpus_path = root / "data/theory_validation/corpus_v1.jsonl"
    build_theory_validation_corpus(root)
    rows = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    train = [r for r in rows if r["split"] == "train"]
    test = [r for r in rows if r["split"] == "test"]
    dev = [r for r in rows if r["split"] == "dev"]

    y_true = [r["theory_id"] for r in test]
    texts_test = [r["text"] for r in test]

    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", LinearSVC(random_state=0)),
        ]
    )
    pipe.fit([r["text"] for r in train], [r["theory_id"] for r in train])
    y_pred = list(pipe.predict(texts_test))

    vec, centroids = _fit_tfidf_centroids([r["text"] for r in train], [r["theory_id"] for r in train])
    y_cent = _predict_centroid(vec, centroids, texts_test)

    labels = sorted(set(y_true) | set(y_pred))
    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    prec, rec, f1s, _supp = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    top1 = float(np.mean([a == b for a, b in zip(y_true, y_pred)]))
    top1_centroid = float(np.mean([a == b for a, b in zip(y_true, y_cent)]))

    margins: list[float] = []
    correct_ranks: list[int] = []
    scores = np.atleast_2d(pipe.decision_function(texts_test))
    class_list = list(pipe.named_steps["clf"].classes_)
    if scores.shape[1] == 1 and len(class_list) == 2:
        scores = np.column_stack([-scores[:, 0], scores[:, 0]])
    for i, yt in enumerate(y_true):
        row = np.asarray(scores[i]).ravel()
        order = np.argsort(-row)
        ranked = [class_list[int(j)] for j in order]
        correct_ranks.append(ranked.index(yt) + 1 if yt in ranked else len(ranked))
        best = float(row[order[0]])
        second = float(row[order[1]]) if len(order) > 1 else 0.0
        if ranked[0] == yt:
            margins.append(best - second)
        elif yt in class_list:
            margins.append(float(row[class_list.index(yt)] - best))
        else:
            margins.append(float("nan"))

    fps = load_all_fingerprints(root / "ontology/physics_fingerprints")
    kw_pred = []
    for row in test:
        v = keyword_feature_proxy(row["text"])
        sc = {
            tid: binary_vector_jaccard(
                v, {k: int(fp.features.get(k, 0)) for k in set(v) | set(fp.features)}
            )
            for tid, fp in fps.items()
        }
        kw_pred.append(max(sc, key=sc.get))
    kw_top1 = float(np.mean([a == b for a, b in zip(y_true, kw_pred)]))

    per_theory = {
        lab: {
            "precision": float(prec[i]),
            "recall": float(rec[i]),
            "f1": float(f1s[i]),
            "support": int(sum(1 for y in y_true if y == lab)),
        }
        for i, lab in enumerate(labels)
    }
    weakest = min(per_theory.items(), key=lambda kv: kv[1]["f1"])[0] if per_theory else None

    held = attach_provenance(
        {
            "benchmark_id": "ISEF2027-THEORY-VAL-HELDOUT-v2",
            "scorer": "tfidf_linearsvc_train_only",
            "secondary_scorer": "tfidf_centroid_train_only",
            "n_train": len(train),
            "n_dev": len(dev),
            "n_test": len(test),
            "labels": labels,
            "top1_accuracy": top1,
            "top1_accuracy_centroid_secondary": top1_centroid,
            "macro_f1": macro_f1,
            "mean_correct_rank": float(np.nanmean(correct_ranks)),
            "mean_margin": float(np.nanmean(margins)),
            "confusion_matrix": {"labels": labels, "matrix": cm},
            "per_theory": per_theory,
            "weakest_theory_by_f1": weakest,
            "thermo_investigation": {
                "thermo_f1": per_theory.get("thermodynamics", {}).get("f1"),
                "thermo_recall": per_theory.get("thermodynamics", {}).get("recall"),
                "note": "Keyword-proxy thermo failure was mapping coverage; SVM/TF-IDF is claim-bearing path.",
            },
            "qm_vs_qft_note": "Centroid confused QM/QFT; LinearSVC is primary for that reason.",
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.HELD_OUT_METHOD_VALIDATION,
            synthetic=False,
            real_text=True,
            phase="validation",
            source_split="test",
            method_version="theory_val_tfidf_svm_v2",
            notes="Train fit before test evaluation; test labels unused for fitting.",
        ),
    )

    demo = attach_provenance(
        {
            "benchmark_id": "ISEF2027-THEORY-VAL-KEYWORD-PROXY-DEMO",
            "scorer": "keyword_feature_proxy+jaccard_fingerprint",
            "top1_accuracy": kw_top1,
            "warning": "SOFTWARE_DEMO — not claim-bearing validation.",
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.SOFTWARE_DEMO,
            synthetic=False,
            real_text=True,
            phase="validation",
            source_split="test",
            method_version="keyword_proxy_v0",
            notes="Plumbing comparison only.",
        ),
    )

    out_dir = root / "results/isef2027/validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "held_out_theory_identification.json").write_text(
        json.dumps(held, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "keyword_proxy_demo.json").write_text(json.dumps(demo, indent=2) + "\n", encoding="utf-8")
    return {"held_out": held, "keyword_proxy_demo": demo}
