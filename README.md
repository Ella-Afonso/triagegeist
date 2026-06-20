# Triagegeist: Auditing When Synthetic Emergency Department Triage Benchmarks Hide Residual Risk Signal

**Triagegeist** is a three-dataset benchmark audit of emergency department triage labels as predictors of patient outcomes. The project applies a consistent modelling and evaluation protocol to a synthetic emergency department dataset, **NHAMCS 2022**, and **MIMIC-IV-ED** in order to test whether triage-time features provide meaningful outcome signal beyond the assigned acuity label.

The central finding is that the synthetic benchmark produces a largely negative result: once triage acuity is known, additional triage-time features add only limited predictive value. However, this finding does not replicate on either real-data source. In both NHAMCS 2022 and MIMIC-IV-ED, triage-time features substantially outperform acuity-only baselines, and MIMIC-IV-ED shows clear residual predictive signal within ESI 3 and ESI 4 bands.

Rather than presenting a deployable clinical model, Triagegeist positions itself as a **benchmark audit and proof-of-concept for safer evaluation of emergency triage AI systems**. The project asks whether a benchmark preserves clinically meaningful feature–outcome relationships, or whether it collapses risk prediction into a simplified severity proxy.

---

## Key finding

On the synthetic dataset, an outcome model that excludes the triage acuity label gains only a small amount of average precision over a triage-acuity-only baseline and loses performance on balanced accuracy and ROC-AUC. Within synthetic acuity bands 3 and 4, the same protocol finds no clear residual signal, with out-of-fold ROC values close to random discrimination.

When the identical audit logic is applied to **NHAMCS 2022** and **MIMIC-IV-ED**, the conclusion changes. Triage-time features outperform the closest available acuity-only baselines: the NHAMCS triage-immediacy label (**IMMEDR**) and the MIMIC-IV-ED **ESI** acuity label. In MIMIC-IV-ED, within-band modelling in ESI 3 and ESI 4 produces clear residual signal for both admission/transfer and long-stay prediction.

This divergence suggests that the synthetic benchmark may under-represent real emergency department risk structure. In practical terms, the synthetic data makes triage-time features appear less informative than they are in real ED datasets. This matters because benchmark design can directly shape how emergency triage AI systems are evaluated, compared, and interpreted.

---

## Repository structure

```text
triagegeist/
├── notebooks/
│   └── triagegeist_submission.ipynb   # judge-facing submission notebook
├── outputs/
│   ├── figures/                       # final figures referenced by the report
│   └── tables/                        # aggregate CSV tables for headline results
├── src/
│   ├── __init__.py
│   └── config.py                      # paths, SEED, and package-version checks
├── docs/                              # project brief and judging rubric notes
├── data/
│   ├── raw/                           # synthetic competition CSVs (gitignored)
│   ├── nhamcs/                        # NHAMCS 2022 files (gitignored)
│   ├── mimic/                         # credentialed MIMIC-IV-ED files (gitignored)
│   └── processed/                     # intermediate caches (gitignored)
├── technical_report.md                # full judge-facing technical report
├── submission_summary.md              # 300–500-word submission summary
├── README.md                          # project overview
├── requirements.txt
└── _*.py                              # internal cache-build and regeneration helpers
```

`notebooks/triagegeist_main.ipynb` is the original working notebook. The judged artefact is `notebooks/triagegeist_submission.ipynb`, which contains the cleaned, judge-facing analysis and is treated as the main source of implementation evidence.

---

## Final submission artefacts

The final submission consists of the following artefacts:

* **Submission notebook:** `notebooks/triagegeist_submission.ipynb`
* **Technical report:** `technical_report.md`
* **Submission summary:** `submission_summary.md`
* **Polished figures:** `outputs/figures/`
* **Aggregate result tables:** `outputs/tables/`

The notebook, report, and summary are designed to be readable independently. The technical report provides the structured interpretation of the project, while the notebook provides the implementation trail, reproducibility checks, figures, and result tables.

---

## Submission compliance

This repository is organised to satisfy the Kaggle write-up submission requirements for the Triagegeist track.

Required submission components:

* **Kaggle Write-up:** the main project report submitted through the Kaggle write-up page and kept within the 2,000-word limit.
* **Cover image:** a 560 × 280 px media gallery image prepared for the Kaggle submission page.
* **Attached public notebook:** `notebooks/triagegeist_submission.ipynb`, the cleaned judge-facing notebook.
* **Attached project link:** this public repository, containing the technical report, submission summary, figures, tables, setup instructions, and reproducibility notes.

The notebook and repository are designed to be publicly accessible without login or paywall restrictions. Credentialed datasets such as MIMIC-IV-ED are not redistributed; only aggregate results, figures, and tables are included.

---

## Data sources

### Synthetic emergency department dataset

The synthetic dataset is the hackathon competition data and includes `train.csv`, `test.csv`, `chief_complaints.csv`, and `patient_history.csv`. The analysis uses a stratified 80/20 train/holdout split with a locked random seed. This dataset is treated as the benchmark under audit.

### NHAMCS 2022

NHAMCS 2022 is the US National Hospital Ambulatory Medical Care Survey emergency department public-use file from the CDC/NCHS archive. It is used to test whether the synthetic benchmark finding replicates on real, weighted US emergency department survey data. Because NHAMCS does not use ESI in the same way as MIMIC-IV-ED, the **IMMEDR** triage-immediacy variable is treated as the closest available acuity analogue.

### MIMIC-IV-ED

MIMIC-IV-ED is a credentialed PhysioNet emergency department dataset from Beth Israel Deaconess Medical Center. It is processed locally and used as a large, granular replication source covering approximately 418,000 ED stays with ESI acuity and triage-time vital signs. Raw MIMIC-IV-ED files are not committed to this repository.

---

## Main results summary

| Dataset     |            Outcome | Acuity-only AP | Outcome model AP |   Δ AP | Interpretation                 |
| ----------- | -----------------: | -------------: | ---------------: | -----: | ------------------------------ |
| Synthetic   | Admission/transfer |          0.661 |            0.688 | +0.028 | Limited residual signal        |
| Synthetic   |      Long stay ≥4h |          0.710 |            0.733 | +0.023 | Limited residual signal        |
| NHAMCS 2022 | Admission/transfer |          0.303 |            0.500 | +0.197 | Diverges from synthetic result |
| NHAMCS 2022 |      Long stay ≥4h |          0.503 |            0.608 | +0.104 | Diverges from synthetic result |
| MIMIC-IV-ED | Admission/transfer |          0.635 |            0.808 | +0.173 | Diverges from synthetic result |
| MIMIC-IV-ED |      Long stay ≥4h |          0.752 |            0.838 | +0.086 | Diverges from synthetic result |

In MIMIC-IV-ED, within-band modelling in ESI 3 and ESI 4 produces clear residual signal for both outcomes. For admission/transfer, out-of-fold ROC reaches 0.784 in ESI 3 and 0.814 in ESI 4. In contrast, the synthetic within-band analysis produces no clear residual signal, with out-of-fold ROC values close to 0.50.

The exact result values are available in:

* `outputs/tables/table_final_summary_metrics.csv`
* `outputs/tables/table_mimic_replication.csv`
* `outputs/tables/table_mimic_within_band.csv`

---

## How to review the project

A recommended judge review path is:

1. Read `submission_summary.md` for the concise 300–500-word project narrative.
2. Skim `technical_report.md` for the structured research framing, methods, findings, and limitations.
3. Open `notebooks/triagegeist_submission.ipynb` to inspect the implementation, figures, and reproducibility notes.
4. Spot-check headline numbers in `outputs/tables/table_final_summary_metrics.csv`.

Key summary figures include:

* `fig_summary_pr_contrast.png`
* `fig_summary_audit_panel.png`
* `fig_summary_within_band_signal.png`
* `fig_summary_rate_by_level.png`

---

## Reproducibility notes

The project was developed using **Python 3.10+** on the Anaconda distribution. Reproducibility is supported through locked seeds, explicit package checks, version reporting, and table-driven result generation.

Key reproducibility details:

* Seeds are locked through `src/config.py::seed_everything()`.
* `random`, `numpy`, and `PYTHONHASHSEED` are pinned to `SEED = 42`.
* Package versions are printed in the notebook reproducibility header and listed in `requirements.txt`.
* The submission notebook detects whether it is running on Kaggle or locally and adjusts paths accordingly.
* All headline numbers reported in the README and report are drawn from `outputs/tables/`.
* Figures referenced in the report are stored in `outputs/figures/`.

To run the project locally:

```bash
git clone <your-repo-url>
cd triagegeist
pip install -r requirements.txt
jupyter lab notebooks/triagegeist_submission.ipynb
```

NHAMCS and MIMIC-IV-ED inputs must be obtained separately under their respective access terms. This repository does not redistribute either dataset.

---

## MIMIC-IV-ED and PhysioNet governance note

MIMIC-IV-ED was processed locally under credentialed PhysioNet access. Raw MIMIC-IV-ED files are not included in this repository, and `data/mimic/` is gitignored.

To reduce disclosure risk, the released notebook, report, summary, figures, and tables do not include subject IDs, stay IDs, hospital admission IDs, raw chief complaint text, medication names, or row-level predictions. Only aggregate results are reported.

The strict headline MIMIC-IV-ED model uses triage-time intake features only. Diagnoses, disposition codes, departure time, emergency department length of stay, Pyxis dispensing, and post-triage vitals are excluded from the feature set. This design is intended to reduce target leakage and ensure that the model is evaluated using information plausibly available at triage.

The project is intended for retrospective research and benchmark auditing only. It is not a clinical deployment system.

---

## Limitations

Several limitations should be considered when interpreting the results.

First, the synthetic dataset may not preserve the real joint distribution between triage-time features and patient outcomes. This means that a negative finding on the synthetic benchmark should not automatically be interpreted as evidence that triage-time features lack clinical value.

Second, NHAMCS 2022 uses **IMMEDR**, which is not identical to ESI. The NHAMCS analysis is therefore best interpreted as a real-data replication using the closest available acuity analogue, rather than a direct ESI-to-ESI comparison.

Third, MIMIC-IV-ED is retrospective and single-centre. Although it provides a large and granular emergency department dataset, the findings do not establish generalisability across hospitals, health systems, or prospective clinical workflows.

Fourth, average precision must be interpreted relative to the underlying outcome base rate. For this reason, AP is reported alongside outcome prevalence where appropriate.

Finally, within-band predictive signal demonstrates that residual outcome-relevant information exists among patients with the same acuity label. It does not, by itself, establish clinical utility, safety, fairness, or readiness for deployment.

**Triagegeist should not be used for patient care without prospective validation, local governance review, safety testing, and clinician oversight.**

---

## Author and hackathon note

Triagegeist is a solo entry for the Kaggle-hosted **Triagegeist** track by the **Laitinen-Fredriksson Foundation**. The project is judged by rubric rather than leaderboard position.

Released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
