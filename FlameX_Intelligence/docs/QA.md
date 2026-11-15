# Validation record

## Verified by automated local tests

- Original experimental CSV: 274 rows x 15 columns, included without modification
- Column mapping for uploaded master file, zero source-row deletion, missing data retained
- Methanol and heptane slopes and Brown–Forsythe p match prior rounded report
- Previously reported residual variances do not match exactly under current variance convention: display recalculation explicitly
- Interaction term, anomaly flags, duplicate identifier check and missingness
- Pressure-regime grouped cross-validation; outcome stratified cross-validation
- Exploration-atmosphere and historical-testing reference queries show zero joint coverage; unsupported predictions withheld
- Local TF-IDF NASA evidence retrieval (22 source notes) over FLEX, BASS-II and Saffire-I/II/III; source citation IDs, links, comparisons and unsupported numerical queries tested
- 21 catalog entries, NASA sources included, only FLEX data marked loaded

## Runtime and deployment limitations

The build environment did not have Streamlit installed; a live browser launch could not be performed here. Therefore **an actual launched Streamlit UI/browser smoke test was not performed here**. All Python modules and the app have been syntax-checked. The final suite has 37 science, provenance and conversation tests (37/37 passed in this workspace); rerun with `python -m pytest tests -q`. A mocked interface smoke test executed all nine page branches and Plotly figure construction successfully (9/9). This mock **does not** substitute for actual browser testing on a machine with Streamlit installed.

### Required checks after launch

- [ ] View all pages without Streamlit exceptions.
- [ ] Alter each fuel/outcome/O₂/pressure filter and confirm charts and record counts update.
- [ ] Confirm confidence intervals and regression numbers for the full dataset.
- [ ] Check model regression and classification time/performance and no prob display on reliability failure.
- [ ] Anomaly Hunter: inspect test #114 and view original row intact.
- [ ] FlameIQ: test supported FLEX calculations, multi-investigation source retrieval, evidence library links, and unsupported numerical questions.
- [ ] Export Markdown and HTML research brief, verify labels and source references.
- [ ] Check responsive desktop and tablet layouts in deployed app.
- [ ] Confirm optional LLM disabled by default and no API key in repo.
- [ ] Confirm deployed URL and external NASA source links.

## Known limitations

1. NASA PSI catalog metadata is not a dump of observation-level datasets for the remaining 20 investigations.
2. NASA sources distinguish 8.2 psia / 34% O₂ (exploration atmosphere) from 10.2 psia / 30% O₂ (historical material-flammability screening). Both are source-linked reference POINTS, not a range or validated safety threshold.
3. Physical unit `Burning rate; mm` and `CO` name need original NASA schema confirmation.
4. Pressure-regime grouped CV is exploratory, and its empirical interval is not guaranteed coverage.
5. The outcome classifier uses stratified rather than pressure-grouped validation; not an operational safety classifier.
6. No sensor-level measurement uncertainty supplied in this CSV.
7. Relevance criteria are transparent editorial scores, not causal measurements or safety scores.
8. Only historical FLEX measurements are available; no extrapolation to unrepresented habitat regimes.

## Evidence upgrade verification (2026-11-14)

- Evidence library: 22 separately identified NASA-source paraphrases, with original pages and source sections recorded.
- No non-FLEX observation-level data imported; all original FLEX rows kept unchanged.
- Cross-investigation retrieval tested for FLEX/BASS-II/Saffire and selected topic queries.
- Non-FLEX experimental counts and numerical results are refused instead of substituted with FLEX counts.
- Source URLs are checked for official NASA domains and metadata/library distinction is displayed.
- Run `python -m pytest tests -q` from the project folder.
- Run `PYTHONPATH=. python tests/mock_streamlit_smoke.py` from the project folder (Linux/macOS); on Windows `set PYTHONPATH=.` then `python tests\mock_streamlit_smoke.py`.
- **Not yet tested here:** actual Streamlit browser interactions and responsive layouts.
- The refreshed seven-slide PowerPoint/PDF use documented NASA sources and independently recalculated FLEX findings; add actual deployed URLs when available.

## Final release export check

- Seven-slide PPTX regenerated from the unchanged source CSV.
- Seven-page PDF exported and visually rendered for layout review.
- 37/37 Python tests and 9/9 mocked interface page checks passed.
- Actual public Streamlit hosting and a live OpenAI request remain unverified until deployment.
