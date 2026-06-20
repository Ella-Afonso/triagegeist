# Triagegeist: Auditing When Synthetic Emergency Department Triage Benchmarks Hide Residual Risk Signal

*A three-dataset benchmark audit showing that synthetic emergency department triage data can flatten residual risk signals that reappear in real clinical datasets.*

## Project overview

Triagegeist is a benchmark audit, not a deployed clinical tool. It investigates one empirical question: when a patient arrives at the emergency department, does the recorded triage acuity label already capture most of the outcome-relevant information available at triage, or do triage-time features still contain residual signal beyond that label?

To test this, the same modelling protocol is applied to three datasets: the hackathon synthetic emergency department dataset, NHAMCS 2022, and MIMIC-IV-ED. The aim is not simply to optimise a classifier, but to test whether a synthetic benchmark preserves the same feature–outcome structure seen in real ED data.

## Why this matters

Emergency department triage assigns each patient an acuity category, often using the Emergency Severity Index (ESI), to indicate how urgently the patient should be assessed. However, operational planning depends on a related but different question: what is likely to happen after the triage number is recorded?

Admissions, transfers, and prolonged ED stays affect bed demand, staffing pressure, escalation readiness, and patient flow. If a synthetic benchmark suggests that acuity already captures most of this outcome signal, then outcome-aware triage modelling may appear to offer little additional value. That conclusion becomes risky if it does not replicate on real ED data.

Synthetic data is valuable because it is reproducible and shareable, but it may also simplify or compress the relationship between triage-time features and downstream outcomes. Triagegeist audits that risk directly.

## Method summary

A leakage-safe, stratified 80/20 train/holdout split was created before fitting any preprocessing, with all random seeds locked to `SEED = 42`. Baselines include a majority-class predictor, a NEWS2-only baseline for the synthetic data, and an acuity-only baseline using rate lookup for ROC/AP and hard labels for balanced accuracy.

The primary outcome model is a LightGBM classifier trained with five-fold stratified out-of-fold prediction. Isotonic calibration is applied when it improves Brier loss, thresholds are selected on out-of-fold metrics, and final performance is reported once on the holdout set. For each target, two model variants are trained: an outcome model that excludes acuity, used as the main challenger to the acuity-only baseline, and a companion model that adds acuity as a feature to estimate the remaining upper-bound value.

The same audit logic is applied to NHAMCS using the triage-immediacy label (IMMEDR) as the closest available acuity analogue. For MIMIC-IV-ED, the strict headline model uses only triage-time intake features: vitals, demographics, and TF-IDF features from chief complaint. Average precision (AP) is the primary headline metric because prevalence differs across datasets; ROC-AUC and balanced accuracy are reported alongside it.

## Synthetic benchmark result

On the synthetic dataset, the outcome model without acuity produces only a small AP gain over the triage-acuity-only baseline:

* Admission/transfer: AP **0.688** versus **0.661**, a gain of **+0.028 AP**.
* Long stay, defined as ED length of stay ≥4 hours: AP **0.733** versus **0.710**, a gain of **+0.023 AP**.

However, this improvement does not hold across the complementary metrics. For admission/transfer, the outcome model has lower balanced accuracy, 0.728 versus 0.752, and lower ROC-AUC, 0.804 versus 0.816. For long stay, it also has lower balanced accuracy, 0.783 versus 0.818, and lower ROC-AUC, 0.863 versus 0.873.

The within-band test is the clearest negative result. In synthetic acuity bands 3 and 4, where residual risk stratification would be most operationally relevant, within-band modelling returns uniform **NO_SIGNAL** verdicts with out-of-fold ROC values close to 0.50. Read in isolation, the synthetic benchmark suggests that the acuity label absorbs most outcome-relevant triage information. See `fig_summary_pr_contrast.png`.

## Real-data replication: NHAMCS 2022

When the same protocol is applied to NHAMCS 2022, the conclusion changes.

* Admission/transfer: the outcome model reaches AP **0.500** versus IMMEDR-only AP **0.303**, a gain of **+0.197 AP**. ROC-AUC increases from 0.727 to 0.813, and balanced accuracy increases from 0.649 to 0.731.
* Long stay: the outcome model reaches AP **0.608** versus IMMEDR-only AP **0.503**, a gain of **+0.104 AP**. ROC-AUC increases from 0.642 to 0.706.

Both outcomes therefore diverge from the synthetic benchmark. This comparison is reported cautiously because IMMEDR is not a like-for-like ESI label. Nevertheless, NHAMCS provides important evidence that real ED survey data can retain outcome-relevant triage-time signal that is not captured by the available acuity analogue alone.

## Real-data replication: MIMIC-IV-ED

MIMIC-IV-ED was processed locally under credentialed PhysioNet access. The analysis sample contains approximately 418,000 ED stays from a single centre, Beth Israel Deaconess Medical Center. The strict triage-time LightGBM model substantially outperforms the ESI acuity-only baseline on both outcomes:

* Admission/transfer: AP **0.808** versus **0.635**, a gain of **+0.173 AP**. ROC-AUC increases from 0.711 to 0.823, and balanced accuracy increases from 0.683 to 0.746.
* Long stay: AP **0.838** versus **0.752**, a gain of **+0.086 AP**. ROC-AUC increases from 0.623 to 0.729.

Adding the acuity label as a companion feature produces only modest additional gains, suggesting that much of the improvement comes from triage-time intake information rather than simply re-encoding ESI.

Within-band modelling provides the strongest replication evidence. In ESI 3 and ESI 4, the model detects residual signal for both outcomes:

* Admission/transfer: out-of-fold ROC **0.784** in ESI 3 and **0.814** in ESI 4.
* Long stay: out-of-fold ROC **0.730** in ESI 3 and **0.692** in ESI 4.

This matters operationally because ESI 3 is often treated as a broad middle-acuity category, yet approximately **37%** of ESI-3 stays in the analysis end in admission or transfer. See `fig_summary_within_band_signal.png` and `fig_summary_rate_by_level.png`.

## Main contribution

Across the three datasets, the same audit protocol produces one negative synthetic result and two positive real-data replications. The synthetic dataset yields **REPLICATES_SEVERITY_COLLAPSE** verdicts and **NO_SIGNAL** within-band findings. NHAMCS and MIMIC-IV-ED both yield **DIVERGES** verdicts, while MIMIC-IV-ED additionally shows residual within-band signal across ESI 3 and ESI 4.

The most careful interpretation is that the synthetic dataset compresses outcome variance into the acuity/severity structure more strongly than the real ED datasets do. The contribution is therefore methodological: Triagegeist provides a reproducible framework for testing whether synthetic triage benchmarks preserve clinically meaningful residual outcome signal, rather than assuming that benchmark results automatically transfer to real emergency department settings. See `fig_summary_audit_panel.png`.

## Safety, leakage, and governance

MIMIC-IV-ED was processed locally under credentialed PhysioNet access. Raw MIMIC files are not included in the write-up or repository. No subject IDs, stay IDs, hospital admission IDs, raw chief complaint text, medication names, or row-level predictions appear in the deliverables; only aggregate tables and figures are reported.

The strict headline MIMIC model uses triage-time intake features only. Diagnoses, disposition codes, departure time, ED length of stay, Pyxis medication dispensing, and post-triage vitals are excluded from the feature set. Intake-time medication reconciliation features are treated only as a sensitivity extension because their timing relative to the triage decision is uncertain.

The leakage-safe split is established before preprocessing is fit, and all seeds are locked. These choices are intended to make the benchmark audit reproducible while reducing target leakage and disclosure risk. MIMIC results remain retrospective and single-centre, so they support replication but not clinical validation.

## Limitations

Several limitations are important. The synthetic data may not preserve the true joint distribution between triage-time features and outcomes. NHAMCS uses IMMEDR rather than ESI, so its replication is suggestive rather than a direct ESI comparison. NHAMCS and MIMIC-IV-ED also differ in population, coding, available features, and data-generating process, so cross-dataset agreement should be interpreted structurally rather than statistically.

MIMIC-IV-ED is retrospective and single-centre, and the analysis does not establish prospective effectiveness, fairness, safety, or generalisation to other hospitals. AP must be interpreted relative to outcome prevalence, which is reported alongside the full result tables. Finally, within-band signal demonstrates residual predictive information; it does not by itself prove clinical utility or readiness for deployment.

**Triagegeist is not a clinical deployment system and should not be used for patient care without prospective validation, local governance review, safety testing, and clinician oversight.**

## Conclusion

Triagegeist shows that a synthetic triage benchmark’s negative finding about the value of triage-time features can fail to replicate on real emergency department data. In two real-data replications, triage-time features retain residual outcome signal that acuity alone misses, including within ESI 3 and ESI 4 in MIMIC-IV-ED.

The project contributes a benchmark-audit approach for safer emergency triage AI evaluation: before drawing conclusions from synthetic data, test whether the benchmark preserves the residual clinical signal that matters for real operational planning. Additional PR curves, calibration plots, baseline comparisons, SHAP summaries, and replication figures are included in the submission notebook for detailed review.

## Project files

* Public notebook: `notebooks/triagegeist_submission.ipynb`
* Technical report: `technical_report.md`
* Submission summary: `submission_summary.md`
* Summary tables: `outputs/tables/`
* Final figures: `outputs/figures/`
* Project repository: `https://github.com/Ella-Afonso/triagegeist`
