# Triagegeist: Auditing When Synthetic Emergency Department Triage Benchmarks Hide Residual Risk Signal

## Executive summary

Triagegeist is a three-dataset benchmark audit of emergency department triage labels as predictors of patient outcomes. The project evaluates whether triage-time features provide meaningful outcome signal beyond the assigned acuity label, or whether the acuity label already absorbs most of the information needed to predict downstream outcomes such as admission/transfer and prolonged ED stay.

On the hackathon synthetic dataset, an outcome model that excluded the triage acuity label gained only a small amount of average precision (AP) over an acuity-only baseline and performed worse on balanced accuracy and ROC-AUC. Within synthetic acuity bands 3 and 4, the same modelling approach found no clear residual signal. However, when the identical audit logic was applied to NHAMCS 2022 and MIMIC-IV-ED, the conclusion changed. In both real-data sources, triage-time features substantially outperformed the closest acuity-only baselines, and within-band modelling in MIMIC-IV-ED showed clear residual signal within ESI 3 and ESI 4.

The central contribution is methodological. Triagegeist demonstrates that a synthetic triage benchmark can produce a negative finding about residual risk signal that does not replicate on real emergency department data. The project is therefore framed as a benchmark audit and proof-of-concept for safer emergency triage AI evaluation, not as a deployed clinical system. All results, code, polished figures, and aggregate tables are reproducible from the cleaned submission notebook.

---

## Challenge fit

The Laitinen-Fredriksson Foundation’s Triagegeist track invites well-documented analytical investigations of triage, including prediction tools and clinically relevant data analysis. This project addresses that brief by examining whether benchmark evaluation methodology itself can obscure the relationship between triage labels and patient outcomes.

The project contributes to the **Clinical Relevance** and **Insight & Findings** criteria by focusing on a practical emergency department question: whether patients with the same apparent acuity can still differ meaningfully in their likelihood of admission, transfer, or prolonged ED stay. It addresses **Technical Quality** through leakage-safe splitting, transparent baselines, calibrated LightGBM models, out-of-fold evaluation, SHAP-based interpretation, and cross-dataset replication. Documentation quality is supported by a cleaned judge-facing notebook, a technical report, aggregate output tables, and polished figures stored in `outputs/tables/` and `outputs/figures/`.

---

## Problem definition

Emergency department triage assigns each arriving patient an acuity category, typically using a scale such as ESI 1–5, to indicate how urgently they should be seen. However, operational decision-making depends on a related but different question: what is likely to happen after triage?

A patient’s downstream course may involve admission, transfer, prolonged ED stay, or continued use of scarce department capacity. These outcomes matter for bed planning, escalation readiness, flow management, and staffing pressure. The project therefore asks two empirical questions:

1. Does the acuity label already capture most of the outcome-relevant information available at triage?
2. Is there residual outcome signal within patients assigned to the same acuity band?

The first question is tested through head-to-head comparison between an outcome model that excludes acuity and an acuity-only baseline. The second question is tested through within-band modelling, where models are trained only on patients sharing the same acuity level. This design allows the project to distinguish between models that merely reproduce triage severity and models that identify additional risk structure within triage categories.

---

## Data sources

Three datasets were used.

The **synthetic emergency department dataset** is the hackathon-provided benchmark dataset. After intake feature engineering, it contains 80,000 training rows and 20,000 holdout rows from a stratified split. This dataset provides the reproducible benchmark under audit.

**NHAMCS 2022**, the US National Hospital Ambulatory Medical Care Survey emergency department public-use file, was used as a real-world survey-based replication source. Because NHAMCS does not provide a direct like-for-like ESI structure in the same form as MIMIC-IV-ED, the triage-immediacy label **IMMEDR** was treated as the closest available acuity analogue.

**MIMIC-IV-ED** was used as a large, granular real-data replication source. It is a credentialed PhysioNet dataset from Beth Israel Deaconess Medical Center and contains approximately 418,000 emergency department stays with ESI acuity and triage-time vital signs. MIMIC-IV-ED was processed locally, and raw credentialed data were not redistributed.

Across all three datasets, the project focuses on two outcome targets: admission/transfer at disposition and long ED stay, defined as length of stay of at least four hours. The datasets differ in population, coding, available features, and data-generating process. This heterogeneity is intentional: the aim is not to force the datasets into identical form, but to test whether the same audit logic produces structurally consistent conclusions across synthetic and real ED data.

---

## Methodology

A leakage-safe stratified train/holdout split was created before any preprocessing was fit. The synthetic analysis used an 80/20 split with all random seeds locked to `SEED = 42`; the same split-before-preprocessing convention was applied to NHAMCS and MIMIC-IV-ED.

The baseline models include a majority-class predictor, a NEWS2-only baseline for the synthetic dataset, and an acuity-only baseline. The acuity-only baseline uses rate lookup for ROC-AUC and AP, and a hard-label version for balanced accuracy. These baselines are important because the project is not only asking whether a model can predict outcomes, but whether it adds value beyond simple triage severity proxies.

The primary outcome model is a LightGBM classifier trained with five-fold stratified out-of-fold prediction. Isotonic calibration is applied when it improves Brier loss, thresholds are selected on out-of-fold metrics, and final evaluation is performed once on the holdout set. For each outcome target, two model variants are trained:

- an outcome model that excludes the acuity label, used as the main challenger to the acuity-only baseline;
- a companion model that includes acuity as an additional feature, used as an upper-bound reference.

For NHAMCS, the same protocol is applied using IMMEDR as the closest available acuity analogue. For MIMIC-IV-ED, the strict headline model is restricted to triage-time intake features: vital signs, demographics, and TF-IDF features from chief complaint. An extended-intake variant adds medication family information as a sensitivity analysis, because the timing of medication reconciliation relative to triage may be uncertain.

Average precision is used as the primary headline metric because outcome prevalence differs across datasets and AP is sensitive to ranking performance in imbalanced prediction tasks. ROC-AUC and balanced accuracy are reported alongside AP to provide complementary views of discrimination and thresholded classification performance.

---

## Synthetic benchmark results

On the synthetic dataset, the outcome model without acuity achieved only small gains over the triage-acuity-only baseline on AP:

- admission/transfer AP increased from **0.661** to **0.688**, a gain of **+0.028**;
- long-stay AP increased from **0.710** to **0.733**, a gain of **+0.023**.

However, these AP gains did not translate into consistent improvement across the other metrics. For admission/transfer, balanced accuracy decreased from **0.752** to **0.728**, and ROC-AUC decreased from **0.816** to **0.804**. For long stay, balanced accuracy decreased from **0.818** to **0.783**, and ROC-AUC decreased from **0.873** to **0.863**.

Calibration had limited effect. After isotonic adjustment, Brier loss remained at **0.169** for admission/transfer and improved only slightly from **0.142** to **0.141** for long stay.

The most important synthetic finding comes from the within-band analysis. Within synthetic acuity bands 3 and 4, where residual risk stratification would be operationally most relevant, the model produced uniform **NO_SIGNAL** verdicts, with out-of-fold ROC values clustered around **0.50**. Read in isolation, the synthetic benchmark suggests that the acuity label, derived from the embedded NEWS2 severity structure, already absorbs most of the outcome-relevant information available at triage.

Relevant figures include `fig_baseline_longstay.png`, `fig_h2h_longstay.png`, `fig_circularity_exhibit.png`, and `fig_calibration_admitted.png`.

---

## NHAMCS 2022 real-data replication

When the same audit protocol was applied to NHAMCS 2022, the result diverged from the synthetic benchmark.

For admission/transfer, the outcome model excluding IMMEDR achieved AP **0.500**, compared with **0.303** for the IMMEDR-only baseline. This corresponds to a gain of **+0.197 AP**. ROC-AUC increased from **0.727** to **0.813**, and balanced accuracy increased from **0.649** to **0.731**.

For long stay, the outcome model achieved AP **0.608**, compared with **0.503** for the IMMEDR-only baseline, giving a gain of **+0.104 AP**. ROC-AUC increased from **0.642** to **0.706**.

Both NHAMCS outcomes therefore diverged from the synthetic benchmark’s negative finding. This comparison is interpreted cautiously because IMMEDR is not identical to ESI. Nevertheless, NHAMCS provides real-data evidence that outcome-relevant triage-time signal can remain outside the available acuity analogue.

NHAMCS uses patient-visit survey weights for nationally representative population estimates. The modelling AP values reported here are computed on the constructed analysis sample, while survey weighting is noted where relevant for population-level interpretation.

Relevant figures include `fig_nhamcs_pr_admitted.png` and `fig_nhamcs_pr_longstay.png`.

---

## MIMIC-IV-ED real-data replication

MIMIC-IV-ED provided the strongest real-data replication. The analysis included **418,100** admission/transfer-eligible stays with a base rate of **0.480**, and **416,853** long-stay-eligible stays with a base rate of **0.692**.

The strict triage-time LightGBM model substantially outperformed the ESI acuity-only baseline on both outcomes.

For admission/transfer, AP increased from **0.635** to **0.808**, a gain of **+0.173 AP**. ROC-AUC increased from **0.711** to **0.823**, and balanced accuracy increased from **0.683** to **0.746**.

For long stay, AP increased from **0.752** to **0.838**, a gain of **+0.086 AP**. ROC-AUC increased from **0.623** to **0.729**.

Adding the acuity label as a companion feature produced only modest further gains. This suggests that much of the improvement comes from triage-time intake features rather than simply re-encoding ESI acuity.

Within-band modelling provided further evidence of residual risk signal. In ESI 3 and ESI 4, the model produced clear **SIGNAL** verdicts for both outcomes:

- admission/transfer: out-of-fold ROC **0.784** in ESI 3 and **0.814** in ESI 4;
- long stay: out-of-fold ROC **0.730** in ESI 3 and **0.692** in ESI 4.

The under-triage exhibit shows why this matters operationally. Within ESI 3 alone, approximately **37%** of stays ended in admission or transfer, with **n ≈ 224,652**. This does not imply that the ESI label is wrong, but it does show that a broad middle-acuity category can contain substantial variation in downstream resource need.

Relevant figures include `fig_mimic_pr_admitted.png`, `fig_mimic_pr_longstay.png`, `fig_mimic_undertriage.png`, and `fig_summary_within_band_signal.png`.

---

## Cross-dataset synthesis

The same audit protocol produced one negative synthetic result and two positive real-data replications.

On the synthetic dataset, the results support **REPLICATES_SEVERITY_COLLAPSE** verdicts for both outcomes and uniform **NO_SIGNAL** findings within acuity bands 3 and 4. On NHAMCS 2022 and MIMIC-IV-ED, the results produce **DIVERGES** verdicts for both outcomes. In MIMIC-IV-ED, the within-band analysis additionally produces **SIGNAL** in all four ESI 3/4 outcome evaluations.

The most careful interpretation is that the synthetic dataset compresses outcome variance into the acuity/severity structure more strongly than the real ED datasets do. In other words, the synthetic benchmark makes triage-time features appear less informative than they are in the real-data replications. This matters because benchmark design can influence whether emergency triage AI systems are judged as useful, redundant, or unsafe.

Triagegeist therefore provides evidence that synthetic triage benchmarks can hide clinically meaningful residual outcome signal. The contribution is not a deployed prediction tool, but a reproducible benchmark-audit framework for testing whether synthetic datasets preserve the residual clinical signal that matters for real emergency department planning.

Relevant figures include `fig_summary_pr_contrast.png`, `fig_summary_audit_panel.png`, and `fig_summary_rate_by_level.png`.

---

## Leakage, governance, and safety controls

MIMIC-IV-ED was processed locally under credentialed PhysioNet access. Raw MIMIC files were not exported into the report, notebook, repository, or public deliverables. No subject IDs, stay IDs, hospital admission IDs, raw chief complaint text, medication names, or row-level predictions are included. Only aggregate figures and tables are reported.

The strict headline MIMIC-IV-ED model uses triage-time intake features only: vital signs, demographics, and chief complaint TF-IDF. All post-triage or outcome-adjacent variables are excluded, including diagnoses, disposition codes, departure time, ED length of stay, Pyxis medication dispensing, and post-triage vital signs. Intake-time medication reconciliation features are treated only as a sensitivity extension because their timing relative to triage may not be fully certain.

The leakage-safe split is established before preprocessing is fit, and seeds are locked at `SEED = 42`. These choices are intended to make the audit reproducible while reducing target leakage, post-outcome contamination, and disclosure risk. The MIMIC-IV-ED results remain retrospective and single-centre, so they support replication of the audit pattern but do not establish clinical validation.

---

## Limitations

Several limitations bound the claims made by this project.

First, synthetic data may not preserve the true joint distribution between triage-time features and patient outcomes in real emergency departments. Therefore, the synthetic result should not be interpreted as definitive evidence that triage-time features lack value.

Second, NHAMCS 2022 uses IMMEDR rather than ESI. The NHAMCS replication is therefore suggestive of real-data divergence, but it is not a like-for-like ESI comparison.

Third, NHAMCS and MIMIC-IV-ED differ in feature structure, coding practice, population, and data-generating process. Cross-dataset agreement should therefore be interpreted structurally rather than statistically.

Fourth, MIMIC-IV-ED is retrospective and single-centre. The analysis does not establish prospective safety, effectiveness, fairness, or generalisation to other hospitals and health systems.

Fifth, AP must be interpreted relative to outcome prevalence. For this reason, the project reports outcome base rates alongside the full AP results.

Finally, within-band signal demonstrates residual predictive information. It does not, by itself, establish clinical utility, workflow benefit, or readiness for deployment.

Triagegeist is not a clinical deployment system and should not be used for patient care without prospective validation, local governance review, safety testing, and clinician oversight.

---

## Future work

Future work should evaluate whether the audit findings remain stable across time, sites, and patient subgroups. A natural next step would be a prospective or temporally held-out evaluation, followed by replication on a second hospital system to test cross-site generalisation.

The within-band audit could also be extended to additional operational outcomes, such as 72-hour return, short-interval admission, escalation after discharge, or intensive care transfer. A calibrated subgroup audit would be important to test whether residual within-band signal is distributed fairly or concentrated in clinically sensitive groups.

Finally, any applied version of this work should be evaluated as a clinician-in-the-loop decision-support prototype rather than as an autonomous triage system. The appropriate next stage is therefore not direct deployment, but careful workflow simulation, local governance review, prospective validation, and safety monitoring.

---

## Conclusion

Triagegeist provides evidence that a synthetic triage benchmark’s negative finding about the value of triage-time features can fail to replicate on real emergency department data. In NHAMCS 2022 and MIMIC-IV-ED, triage-time features retain residual outcome signal beyond the available acuity label, including within ESI 3 and ESI 4 in MIMIC-IV-ED.

The project’s contribution is methodological: it offers a small, reproducible, three-dataset audit for testing whether synthetic emergency triage benchmarks preserve clinically meaningful residual outcome signal. Triagegeist does not replace triage, does not provide a deployed clinical model, and should not be used for patient care without prospective validation and clinician oversight.