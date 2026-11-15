# Submission-ready wording — FlameX Intelligence

## Project name
**FlameX Intelligence**

## One-line description
An evidence-aware research dashboard that turns NASA microgravity combustion investigations into traceable findings while making uncertainty and missing data visible.

## Summary (approx. 150 words)

Spacecraft fire safety depends on research that spans liquid droplets, solid materials, large-scale fires, and smoke detection. These experiments are difficult to compare because they use different measurements and conditions. **FlameX Intelligence** brings the research into one interactive, source-linked workspace.

Our dashboard analyzes a 274-record FLEX experimental table, recomputes fuel-specific relationships and uncertainty tests, and flags where a model or scenario lacks supporting observations. A seven-investigation NASA PSI registry links users to BASS-II, Saffire, SAME, and other primary sources. The new Data Lab can audit additional original NASA experimental-table CSVs without silently merging incompatible studies. FlameIQ connects questions to NASA evidence, numerical calculations, and clear explanations of what remains unknown. Its default mode works without an AI API key; optional hosted language-model support is separated from verified research findings.

FlameX is a research interpretation tool, not an operational spacecraft fire-safety decision system. It helps future investigators see both what NASA has measured and what needs better evidence.

## Impact statement
FlameX makes source selection, reproducibility, and evidence gaps visible. Its immediate contribution is to research navigation and methodological transparency; measurable real-world risk reduction has not been validated.

## Technical approach
Python, Streamlit, pandas, SciPy, statsmodels, scikit-learn, Plotly, TF-IDF evidence retrieval. Original FLEX source rows are retained and fingerprinted. Experimental sources are cataloged separately. Additional NASA PSI tables are audited one column at a time, preserving qualifiers and unknown units. Regression/classification models are exploratory and internally evaluated, not externally validated fire-safety predictors.

## AI use disclosure
AI tools assisted with writing, code generation/review and presentation design. FlameIQ's built-in evidence search is deterministic retrieval with scientific calculation tools, not an unbounded language model. Optional hosted text models may help phrase research answers but are not a source of additional experimental facts. No unverified generated observations were added.

## Important limitation
The ZIP bundles original FLEX observations only. Official NASA PSI metadata links are included for BASS-II, Saffire, SAME and others, but those experiment-level raw files are **not** bundled. Their original downloads need to be obtained and authenticated separately before claiming cross-investigation quantitative findings.
