# Science audit: traceability before conclusions

## Data origin

The bundled data are the original team-provided 274-row, 15-column FLEX CSV. That file's hash is shown in the application. NASA PSI-69 is the intended investigation reference, but matching the team's file byte-for-byte to a NASA original export was not possible here; the provenance note must remain explicit.

Other referenced NASA PSI investigation pages were independently located and their available metadata verified, including BASS-II PSI-25, Saffire-I PSI-98, Saffire-II PSI-99, SAME-R PSI-101 and SAME PSI-102. The external original experimental files could not be downloaded in this build environment, so **no other raw-data rows were imported or synthesized**.

## Why the raw-data importer does not pool studies

A column named “rate” or “O₂” in different experiment tables does not imply identical physical meaning, units, instruments, or boundary conditions. The Data Lab retains original column names and values, labels approximate or qualified cells, and computes summaries only inside a *single selected source column*. Independently checking metadata, preprocessing and repeatability would be needed before any harmonized multi-study model.

## Calculation limits

The FLEX statistics compare two fuel-specific OLS fits on nonmissing data. The slope comparison does not establish equivalence. The Brown–Forsythe residual test concerns variance in model errors, not flame stability in the physical sense. Test-end categories are source labels, not a validated hazard scale. Unmeasured instrument uncertainty must not be confused with observed model residuals.

## Model status

Cross-validation metrics reflect performance on the supplied table and chosen splits, not external validity. Prediction is deliberately gated when the scenario is outside relevant observed support. Atmosphere-reference checks are research-coverage diagnostics, not safety thresholds.

## AI status

The default assistant uses deterministic calculations and a 22-entry NASA-linked paraphrase library. Retrieval is a way to locate evidence; it does not turn metadata into numerical observations. External LLMs are optional and the live services were not connected in this build environment.
